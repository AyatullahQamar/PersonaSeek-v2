from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from serpapi import GoogleSearch
import re
import os
from dotenv import load_dotenv

from intent_store import match_search_term, get_description, refresh as refresh_intents
from intent_db import init_db, connect
from pydantic import BaseModel

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

app = FastAPI(title="AI Professional Finder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    refresh_intents(force=True)

@app.get("/")
def root():
    return {"status": "PersonaSeek backend is running"}

# -----------------------------
# Admin Models + Endpoints
# -----------------------------
class RuleIn(BaseModel):
    pattern: str
    search_term: str
    priority: int = 100
    enabled: int = 1

class DescIn(BaseModel):
    search_term: str
    description: str

@app.post("/admin/rules")
def add_rule(r: RuleIn):
    with connect() as conn:
        conn.execute(
            "INSERT INTO intent_rules(pattern, search_term, priority, enabled) VALUES (?,?,?,?)",
            (r.pattern, r.search_term, r.priority, r.enabled)
        )
        conn.commit()
    refresh_intents(force=True)
    return {"ok": True}

@app.post("/admin/descriptions")
def upsert_description(d: DescIn):
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO intent_descriptions(search_term, description)
            VALUES (?, ?)
            ON CONFLICT(search_term) DO UPDATE SET description=excluded.description
            """,
            (d.search_term, d.description)
        )
        conn.commit()
    refresh_intents(force=True)
    return {"ok": True}

# -----------------------------
# Core Search
# -----------------------------
def find_people(occupation: str, location: str):
    if not SERPAPI_KEY:
        raise HTTPException(
            status_code=500,
            detail="SERPAPI_KEY missing in backend/.env"
        )

    params = {
        "engine": "google_maps",
        "q": f"{occupation} near {location}",
        "api_key": SERPAPI_KEY
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SerpAPI error: {str(e)}")

    people = []
    for place in results.get("local_results", []):
        people.append({
            "name": place.get("title"),
            "address": place.get("address"),
            "phone": place.get("phone"),
            "rating": place.get("rating"),
            "website": place.get("website"),
            "gps_coordinates": place.get("gps_coordinates"),  # optional useful
            "place_id": place.get("place_id"),              # optional useful
        })
    return people

@app.get("/search")
def search_people(profession: str, location: str):
    return find_people(profession, location)

# -----------------------------
# Chat Flow
# -----------------------------
_sessions: dict[str, dict] = {}

def _infer_search_term(user_text: str) -> str | None:
    t = (user_text or "").strip()
    if not t:
        return None

    term = match_search_term(t)
    if term:
        return term

    if len(t.split()) <= 4 and not re.search(r"\b(i have|i need|problem|issue|help me|looking for)\b", t.lower()):
        return t

    return "local service"

def _describe_problem(problem_text: str, search_term: str) -> str:
    info = get_description(search_term)
    if info:
        return (
            f"📝 I understand: “{problem_text}”.\n"
            f"✅ You likely need **{search_term.title()}**.\n"
            f"ℹ️ {info}\n\n"
            f"📍 Tell me your city and I’ll show real nearby options with address, rating, and contact."
        )
    return f"📍 Which city are you in?"

@app.post("/chat")
def chat(payload: dict):
    chat_id = (payload.get("chatId") or payload.get("chat_id") or "").strip()
    message = (payload.get("message") or "").strip()

    if not chat_id:
        raise HTTPException(status_code=400, detail="chatId is required.")
    if not message:
        return {"reply": "Please type your problem or the service you need."}

    state = _sessions.get(chat_id, {})

    if state.get("awaiting_city"):
        city = message
        search_term = state.get("search_term") or "professionals"
        problem_text = state.get("problem_text") or search_term

        people = find_people(search_term, city)

        _sessions.pop(chat_id, None)
        return {
            "reply": f"Here are **{search_term.title()}** near **{city}** (based on: “{problem_text}”):",
            "results": people
        }

    search_term = _infer_search_term(message)
    _sessions[chat_id] = {
        "awaiting_city": True,
        "problem_text": message,
        "search_term": search_term,
    }

    return {"reply": _describe_problem(message, search_term) + "\n\nWhich city are you in?"}
