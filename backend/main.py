from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from serpapi import GoogleSearch
import re
import json
from openai import OpenAI

import os
from dotenv import load_dotenv
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "PersonaSeek backend is running"}


load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


app = FastAPI(title="AI Professional Finder")

# For local dev, allow everything. In production, set this to your frontend domain(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def find_people(occupation: str, location: str):
    """Existing functionality: returns real local results via SerpAPI Google Maps engine."""
    if not SERPAPI_KEY:
        raise HTTPException(
            status_code=500,
            detail="SERPAPI_KEY is missing. Create backend/.env with SERPAPI_KEY=YOUR_KEY and restart the server."
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
            "website": place.get("website")
        })
    return people

# ✅ Keep OLD endpoint unchanged
@app.get("/search")
def search_people(profession: str, location: str):
    return find_people(profession, location)


# -----------------------------
# NEW: Conversation endpoint
# -----------------------------
# In-memory chat sessions (good for local dev). For production, use Redis/DB.
_sessions: dict[str, dict] = {}

# _INTENT_RULES = [

#     # -------------------------
#     # EMERGENCY / HEALTHCARE
#     # -------------------------
#     (r"\b(ambulance|emergency ambulance)\b", "ambulance service"),
#     (r"\b(er|emergency room|casualty)\b", "emergency hospital"),
#     (r"\b(hospital|clinic|medical center)\b", "hospital"),
#     (r"\b(blood test|cbc|thyroid|lipid|pathology|lab test|diagnostic|diagnostics)\b", "diagnostic center"),
#     (r"\b(x[- ]?ray|mri|ct scan|sonography|ultrasound)\b", "diagnostic imaging center"),
#     (r"\b(pharmacy|chemist|medical store)\b", "pharmacy"),

#     # Doctors by symptom
#     (r"\b(headache|migraine)\b", "neurologist"),
#     (r"\b(fever|cold|cough|flu|body ?ache|weakness|viral)\b", "general physician"),
#     (r"\b(stomach|gas|acidity|indigestion|vomit|diarrhoea|diarrhea|constipation)\b", "gastroenterologist"),
#     (r"\b(chest pain|heart|bp|blood pressure|hypertension|cardiac)\b", "cardiologist"),
#     (r"\b(sugar|diabetes|hba1c)\b", "diabetologist"),
#     (r"\b(kidney|urine infection|uti|stones?|stone|renal)\b", "urologist"),
#     (r"\b(back pain|joint pain|arthritis|knee pain|shoulder pain)\b", "orthopedic doctor"),
#     (r"\b(physio|physiotherapy|rehab)\b", "physiotherapist"),
#     (r"\b(skin|acne|pimples?|rash|eczema|fungal|itch|allergy|hair fall|dandruff)\b", "dermatologist"),
#     (r"\b(tooth|teeth|gum|gums|cavity|root canal|braces|wisdom tooth|toothache|swelling)\b", "dentist"),
#     (r"\b(eye|eyes|vision|blurry|redness|irritation|spectacles|glasses)\b", "eye doctor"),
#     (r"\b(ear|ears|hearing|tinnitus|sinus|throat|tonsil|nose block)\b", "ENT specialist"),
#     (r"\b(pregnan|pregnancy|gynae|gyne|periods?|pcos|women[' ]s health)\b", "gynecologist"),
#     (r"\b(child|baby|newborn|pediatric|vaccination)\b", "pediatrician"),
#     (r"\b(mental|anxiety|depression|stress|therapy|counselling|counseling|psych)\b", "psychologist"),
#     (r"\b(psychiatrist|bipolar|adhd)\b", "psychiatrist"),

#     # -------------------------
#     # MOBILE / COMPUTER / ELECTRONICS REPAIR
#     # -------------------------
#     (r"(?:\bmobile\b|\bphone\b).*(?:\brepair\b|\bfix\b|\bservice\b|\bscreen\b|\bdisplay\b|\bbattery\b)"
#      r"|(?:\brepair\b|\bfix\b|\bservice\b).*(?:\bmobile\b|\bphone\b)"
#      r"|\biphone repair\b|\bandroid repair\b|\bscreen broken\b|\bdisplay broken\b|\bbattery replacement\b",
#      "mobile repair shop"),

#     (r"(?:\blaptop\b|\bcomputer\b|\bpc\b).*(?:\brepair\b|\bfix\b|\bservice\b|\bslow\b|\bformat\b|\bwindows\b|\bvirus\b)"
#      r"|(?:\brepair\b|\bfix\b|\bservice\b).*(?:\blaptop\b|\bcomputer\b|\bpc\b)"
#      r"|\bdata recovery\b|\blaptop screen\b|\bkeyboard replacement\b|\blaptop not working",
#      "computer repair shop"),

#     (r"\b(printer repair|printer not working|ink problem|cartridge)\b", "printer repair"),
#     (r"\b(tv repair|television repair|led tv|lcd tv|smart tv|screen lines)\b", "tv repair"),
#     (r"\b(camera repair|dslr repair)\b", "camera repair"),

#     # -------------------------
#     # HOME APPLIANCE REPAIR
#     # -------------------------
#     (r"\b(ac not cooling|air conditioner|aircon|ac repair|split ac|window ac)\b", "ac repair"),
#     (r"\b(refrigerator|fridge|freezer|cooling issue)\b", "refrigerator repair"),
#     (r"\b(washing machine|washer|dryer|spin problem)\b", "washing machine repair"),
#     (r"\b(microwave|oven|otg)\b", "microwave repair"),
#     (r"\b(geyser|water heater)\b", "geyser repair"),
#     (r"\b(chimney repair|kitchen chimney)\b", "chimney repair"),
#     (r"\b(ro purifier|water purifier|aqua guard|aquaguard)\b", "water purifier service"),

#     # -------------------------
#     # HOME SERVICES / MAINTENANCE
#     # -------------------------
#     (r"\b(leak|water leakage|pipe burst|tap leak|clog|choke|drain|sewer)\b", "plumber"),
#     (r"\b(short circuit|wiring|switch|socket|mcb|fuse|power cut|electric)\b", "electrician"),
#     (r"\b(carpenter|wood work|door repair|furniture repair|cupboard)\b", "carpenter"),
#     (r"\b(paint|painting|wall paint|house paint|painter)\b", "painter"),
#     (r"\b(tiles|tile fitting|marble|granite)\b", "tile contractor"),
#     (r"\b(mason|brick work|plaster|cement work)\b", "mason"),
#     (r"\b(roof leak|waterproofing|damp|seepage)\b", "waterproofing service"),
#     # Roof / ceiling / seepage / waterproofing (put ABOVE plumber)
#     (r"\b(roof|terrace|ceiling)\b.*\b(leak|leaking|seep|seepage|water)\b|\b(leak|leaking|seepage|damp)\b.*\b(roof|terrace|ceiling)\b",
#  "waterproofing service"),

#     (r"\b(damp|seepage|wall damp|paint peel|moisture|water marks)\b",
#  "waterproofing service"),

#     (r"\b(terrace waterproofing|roof waterproofing|bathroom waterproofing)\b",
#  "waterproofing service"),

#     (r"\b(pest|termite|cockroach|bed bugs|rats|mosquito)\b", "pest control"),
#     (r"\b(cleaning|deep cleaning|home cleaning|bathroom cleaning|sofa cleaning)\b", "cleaning service"),
#     (r"\b(packers|movers|shifting|relocation)\b", "packers and movers"),
#     (r"\b(locksmith|lock repair|key duplicate|lost key)\b", "locksmith"),
#     (r"\b(glass work|glass repair|window glass|mirror)\b", "glass contractor"),

#     # -------------------------
#     # SECURITY / AUTOMATION
#     # -------------------------
#     (r"\b(cctv|camera installation|security camera|dvr|nvr)\b", "cctv installation"),
#     (r"\b(alarm system|home security|security system)\b", "security system installer"),
#     (r"\b(smart home|home automation)\b", "home automation service"),

#     # -------------------------
#     # AUTOMOTIVE
#     # -------------------------
#     (r"\b(car repair|garage|mechanic|engine issue|car service)\b", "car mechanic"),
#     (r"\b(bike repair|motorcycle repair|two wheeler service)\b", "bike mechanic"),
#     (r"\b(puncture|tyre puncture|tire puncture|tyre shop|alignment|balancing)\b", "tyre shop"),
#     (r"\b(car wash|detailing|ceramic coating)\b", "car wash"),
#     (r"\b(battery jumpstart|car battery|battery replacement)\b", "car battery shop"),

#     # -------------------------
#     # LEGAL / FINANCE / BUSINESS
#     # -------------------------
#     (r"\b(gst|itr|income tax|tax filing|tds|audit|accounting|bookkeeping)\b", "chartered accountant"),
#     (r"\b(company registration|startup registration|llp|pvt ltd|incorporation)\b", "company registration consultant"),
#     (r"\b(loan|home loan|personal loan|emi|credit score|cibil)\b", "loan consultant"),
#     (r"\b(insurance|policy|claim|health insurance|car insurance)\b", "insurance agent"),
#     (r"\b(money invest|investment|mutual fund|sip|stock broker)\b", "financial advisor"),

#     (r"\b(legal notice|court|case|bail|divorce|property dispute|agreement|drafting|contract)\b", "lawyer"),
#     (r"\b(criminal lawyer|fir|police case)\b", "criminal lawyer"),
#     (r"\b(divorce|maintenance|custody|family dispute)\b", "divorce lawyer"),
#     (r"\b(property|registry|sale deed|land dispute|rent agreement)\b", "property lawyer"),
#     (r"\b(notary|notarize|affidavit)\b", "notary"),
#     (r"\b(trademark|copyright|patent)\b", "intellectual property lawyer"),

#     # -------------------------
#     # REAL ESTATE / CONSTRUCTION / DESIGN
#     # -------------------------
#     (r"\b(real estate|property dealer|broker|buy flat|rent flat)\b", "real estate agent"),
#     (r"\b(architect|house plan|building plan)\b", "architect"),
#     (r"\b(interior|modular kitchen|home design|renovation|false ceiling)\b", "interior designer"),
#     (r"\b(civil engineer|structural engineer)\b", "civil engineer"),
#     (r"\b(contractor|construction|build house)\b", "building contractor"),

#     # -------------------------
#     # EDUCATION / TRAINING
#     # -------------------------
#     (r"\b(tutor|tuition|home tuition|coach|coaching)\b", "tutor"),
#     (r"\b(ielts|toefl|spoken english)\b", "english tutor"),
#     (r"\b(math tutor|physics tutor|chemistry tutor)\b", "home tutor"),
#     (r"\b(guitar|piano|music class)\b", "music teacher"),
#     (r"\b(yoga|zumba|fitness trainer|gym trainer|personal trainer)\b", "personal trainer"),

#     # -------------------------
#     # EVENTS / CREATIVE
#     # -------------------------
#     (r"\b(photography|photoshoot|wedding shoot|prewedding|videography)\b", "photographer"),
#     (r"\b(video editor|editing|reels editor|youtube editor)\b", "video editor"),
#     (r"\b(makeup artist|bridal makeup|salon|hair stylist)\b", "makeup artist"),
#     (r"\b(event planner|wedding planner|decorator|decoration)\b", "event planner"),
#     (r"\b(caterer|catering|food for party)\b", "caterer"),
#     (r"\b(dj|sound system)\b", "dj service"),

#     # -------------------------
#     # DIGITAL / IT SERVICES
#     # -------------------------
#     (r"\b(website|web site|webdev|wordpress|shopify|frontend|backend|developer|web developer)\b", "web developer"),
#     (r"\b(app developer|android developer|ios developer|mobile app)\b", "app developer"),
#     (r"\b(digital marketing|seo|social media marketing|ads|google ads|meta ads)\b", "digital marketing agency"),
#     (r"\b(graphic design|logo design|branding|poster design)\b", "graphic designer"),
#     (r"\b(ui ux|ui/ux|ux designer|product designer)\b", "ui ux designer"),
#     (r"\b(content writer|copywriter|blog writer)\b", "content writer"),

#     # -------------------------
#     # TRAVEL / LOGISTICS
#     # -------------------------
#     (r"\b(travel agent|tour package|holiday package|visa)\b", "travel agent"),
#     (r"\b(taxi|cab|car on rent|driver)\b", "taxi service"),
#     (r"\b(courier|parcel|delivery service)\b", "courier service"),

#     # -------------------------
#     # BEAUTY / WELLNESS
#     # -------------------------
#     (r"\b(spa|massage|salon)\b", "salon"),
#     (r"\b(barber|haircut)\b", "barber shop"),
#     (r"\b(beautician|facial|waxing)\b", "beautician"),

#     # -------------------------
#     # FOOD / HOME HELP
#     # -------------------------
#     (r"\b(cook|chef|home cook|tiffin|meal service)\b", "tiffin service"),
#     (r"\b(bakery|cake order|birthday cake)\b", "bakery"),
#     (r"\b(babysitter|nanny)\b", "nanny service"),
#     (r"\b(maid|house help|domestic help)\b", "maid service"),

#     # -------------------------
#     # GENERAL FALLBACKS (keep at end)
#     # -------------------------
#     (r"\b(repair|fix|service center|maintenance)\b", "repair service"),
#     (r"\b(consultant|advisor)\b", "consultant"),
#     (r"\b(gym|fitness|workout|bodybuilding|weight training)\b", "gym"),

# ]
_TERM_DESCRIPTIONS = {
    # health
    "general physician": "General physicians handle common issues like fever, cold, body pain, weakness, and basic diagnosis.",
    "dentist": "Tooth or gum problems can be due to cavities, infection, sensitivity, or gum inflammation. A dentist can examine and treat it.",
    "dermatologist": "Skin issues like acne, rashes, itching, fungal infections, or hair problems are treated by a dermatologist.",
    "eye doctor": "Eye irritation, redness, blurry vision, or vision check-ups are handled by an eye specialist.",
    "ent specialist": "Ear, nose, throat issues like sinus, throat pain, ear pain, or hearing problems are treated by an ENT specialist.",
    "gynecologist": "Women’s health concerns like periods, pregnancy-related care, or hormonal issues are handled by a gynecologist.",
    "pediatrician": "Child and baby health issues, vaccinations, and growth-related concerns are handled by a pediatrician.",
    "physiotherapist": "Physiotherapy helps in muscle/joint pain, posture issues, injury recovery, and improving movement.",
    "orthopedic doctor": "Bone, joint, back, knee, or shoulder pain is typically handled by an orthopedic specialist.",

    # repairs / electronics
    "mobile repair shop": "Mobile issues like screen damage, battery drain, charging problems, or speaker/mic faults are usually fixed by a mobile repair shop.",
    "computer repair shop": "Laptop/PC issues like slow performance, OS problems, heating, hardware faults, or data recovery are handled by computer repair experts.",
    "tv repair": "TV problems like display lines, no power, sound issues, or panel faults are handled by TV repair technicians.",

    # home services
    "plumber": "Plumbing problems like leaks, clogged drains, tap issues, or pipe damage should be fixed early to avoid water damage.",
    "electrician": "Electrical issues like wiring faults, short circuits, switch/socket problems, or MCB trips should be checked by an electrician for safety.",
    "ac repair": "AC not cooling often happens due to gas leakage, dirty filters, or compressor/fan issues. An AC technician can diagnose and repair it.",
    "cleaning service": "Deep cleaning helps with dust, stains, bathroom/kitchen cleaning, and sofa/carpet cleaning for better hygiene.",
    "pest control": "Pest control helps remove cockroaches, termites, bed bugs, rats, and mosquitoes safely.",

    # professional services
    "chartered accountant": "For GST, ITR, TDS, audits, or accounting work, a Chartered Accountant can handle filings and compliance.",
    "lawyer": "Legal issues like notices, agreements, property disputes, or court matters can be guided by a lawyer.",
    "real estate agent": "Real estate agents help with buying, selling, or renting property and finding suitable options quickly.",

    # digital / creative
    "web developer": "If you need a website, fixes, redesign, or new features, a web developer can build and maintain it.",
    "app developer": "App developers build or fix Android/iOS apps, add features, and publish updates.",
    "digital marketing agency": "Digital marketing includes SEO, social media, ads, and lead generation to grow your business online.",
    "graphic designer": "Graphic designers create logos, posters, branding, banners, and social media creatives.",
    "photographer": "Photographers help with weddings, events, portraits, product shoots, and professional photos.",
    "video editor": "Video editors can edit reels, YouTube videos, wedding videos, add effects, and improve quality.",
    "interior designer": "Interior designers help plan space, decor, modular kitchen, lighting, and full home/office design.",

    # logistics / others
    "packers and movers": "Packers & movers help with shifting household/office items safely with packing and transport.",
    "taxi service": "Taxi services provide local travel, outstation rides, and driver-on-demand options.",
    "travel agent": "Travel agents help with bookings, visa guidance, and tour packages.",
}


_INTENT_RULES = [

# ================= EMERGENCY =================
(r"\b(ambulance|emergency)\b","ambulance service"),
(r"\b(police)\b","police station"),
(r"\b(fire)\b","fire station"),

# ================= MEDICAL =================
(r"\b(fever|cold|cough|flu|weakness|body ache)\b","general physician"),
(r"\b(headache|migraine)\b","neurologist"),
(r"\b(stomach|gas|acidity|vomit|diarrhea|constipation)\b","gastroenterologist"),
(r"\b(tooth|gum|cavity|toothache|braces)\b","dentist"),
(r"\b(skin|acne|rash|fungal|itch|hair fall)\b","dermatologist"),
(r"\b(eye|vision|blur|spectacles)\b","eye doctor"),
(r"\b(ear|nose|throat|sinus)\b","ent specialist"),
(r"\b(baby|child|vaccination)\b","pediatrician"),
(r"\b(pregnancy|periods|pcos|women)\b","gynecologist"),
(r"\b(stress|anxiety|depression)\b","psychologist"),
(r"\b(mental)\b","psychiatrist"),
(r"\b(bone|joint|knee|back pain)\b","orthopedic doctor"),
(r"\b(diabetes|sugar)\b","diabetologist"),
(r"\b(heart|bp|cardiac)\b","cardiologist"),

# ================= FITNESS =================
(r"\b(gym|fitness|workout|bodybuilding)\b","gym"),
(r"\b(yoga)\b","yoga class"),
(r"\b(zumba)\b","zumba class"),
(r"\b(personal trainer)\b","personal trainer"),

# ================= ELECTRONICS =================
(r"\b(mobile|phone).*(repair|fix)\b","mobile repair shop"),
(r"\b(laptop|computer).*(repair|slow|format)\b","computer repair shop"),
(r"\b(tv repair|led tv|lcd tv)\b","tv repair"),
(r"\b(printer)\b","printer repair"),
(r"\b(camera repair)\b","camera repair"),

# ================= HOME APPLIANCES =================
(r"\b(ac|air conditioner)\b","ac repair"),
(r"\b(fridge|refrigerator)\b","refrigerator repair"),
(r"\b(washing machine)\b","washing machine repair"),
(r"\b(microwave|oven)\b","microwave repair"),
(r"\b(geyser)\b","geyser repair"),

# ================= HOME SERVICES =================
(r"\b(plumbing|leak|tap|pipe)\b","plumber"),
(r"\b(electric|switch|socket|mcb)\b","electrician"),
(r"\b(carpenter|door|furniture)\b","carpenter"),
(r"\b(paint|painting)\b","painter"),
(r"\b(cleaning|deep cleaning)\b","cleaning service"),
(r"\b(pest|rats|mosquito|cockroach|termite)\b","pest control"),
(r"\b(lock|key)\b","locksmith"),
(r"\b(glass|mirror)\b","glass contractor"),

# ================= AUTOMOTIVE =================
(r"\b(car repair|garage)\b","car mechanic"),
(r"\b(bike repair)\b","bike mechanic"),
(r"\b(puncture|tyre)\b","tyre shop"),
(r"\b(car wash)\b","car wash"),

# ================= LEGAL / FINANCE =================
(r"\b(lawyer|legal|court|divorce)\b","lawyer"),
(r"\b(gst|itr|tax)\b","chartered accountant"),
(r"\b(loan|emi)\b","loan consultant"),
(r"\b(insurance)\b","insurance agent"),

# ================= PROPERTY =================
(r"\b(real estate|buy flat|rent)\b","real estate agent"),
(r"\b(interior|modular kitchen)\b","interior designer"),
(r"\b(architect)\b","architect"),

# ================= EDUCATION =================
(r"\b(tutor|tuition)\b","home tutor"),
(r"\b(ielts|spoken english)\b","english tutor"),
(r"\b(guitar|music)\b","music teacher"),

# ================= EVENTS =================
(r"\b(photo|photography)\b","photographer"),
(r"\b(video editor)\b","video editor"),
(r"\b(makeup|salon)\b","salon"),
(r"\b(event|wedding planner)\b","event planner"),
(r"\b(caterer)\b","caterer"),
(r"\b(dj)\b","dj service"),

# ================= IT =================
(r"\b(website|web developer)\b","web developer"),
(r"\b(app developer)\b","app developer"),
(r"\b(seo|digital marketing)\b","digital marketing agency"),
(r"\b(graphic design|logo)\b","graphic designer"),

# ================= TRAVEL =================
(r"\b(flight|air ticket)\b","travel agent"),
(r"\b(taxi|cab)\b","taxi service"),
(r"\b(hotel booking)\b","travel agent"),

# ================= FOOD =================
(r"\b(tiffin|home food)\b","tiffin service"),
(r"\b(bakery|cake)\b","bakery"),

# ================= PET =================
(r"\b(vet|dog|cat)\b","veterinary clinic"),

# ================= DEFAULT =================
(r"\b(repair|service)\b","repair service"),

# ================= GOVERNMENT / DOCUMENTS =================
(r"\b(passport|renew passport)\b","passport office"),
(r"\b(pan card)\b","pan card center"),
(r"\b(aadhaar|aadhar)\b","aadhaar enrollment center"),
(r"\b(driving license|dl)\b","rto office"),
(r"\b(voter id)\b","election office"),
(r"\b(birth certificate|death certificate)\b","municipal office"),

# ================= BANKING =================
(r"\b(bank account|open account)\b","bank"),
(r"\b(atm)\b","atm"),
(r"\b(cash deposit)\b","bank"),
(r"\b(locker)\b","bank locker"),

# ================= TELECOM =================
(r"\b(sim card|mobile network)\b","mobile service provider"),
(r"\b(broadband|wifi|internet connection)\b","internet service provider"),

# ================= COURIER =================
(r"\b(parcel|courier|delivery)\b","courier service"),

# ================= PRINTING =================
(r"\b(print|xerox|photocopy|lamination)\b","print shop"),
(r"\b(banner|flex printing)\b","printing service"),

# ================= JOBS / HR =================
(r"\b(job|recruitment|hire staff)\b","recruitment agency"),

# ================= CLOUD / DATA =================
(r"\b(server|cloud hosting|aws|azure)\b","cloud service provider"),
(r"\b(data recovery|hard disk recovery)\b","data recovery service"),

# ================= SECURITY =================
(r"\b(security guard|bouncer)\b","security agency"),

# ================= AGRICULTURE =================
(r"\b(fertilizer|pesticide|seeds)\b","agriculture store"),

# ================= SOLAR / EV =================
(r"\b(solar panel|solar installation)\b","solar installer"),
(r"\b(ev charging|electric vehicle charging)\b","ev charging station"),

# ================= WAREHOUSE =================
(r"\b(storage|warehouse|godown)\b","warehouse"),

# ================= STUDY =================
(r"\b(iit|neet|jee coaching)\b","coaching institute"),
(r"\b(study abroad|foreign education)\b","study abroad consultant"),

# ================= IMMIGRATION =================
(r"\b(visa|immigration)\b","immigration consultant"),

# ================= ASTROLOGY =================
(r"\b(astrologer|kundli|horoscope)\b","astrologer"),

# ================= MATRIMONIAL =================
(r"\b(matrimony|marriage bureau)\b","matrimonial service"),

# ================= FUNERAL =================
(r"\b(funeral|cremation)\b","funeral service"),

# ================= OLD AGE =================
(r"\b(old age home|elder care)\b","elder care service"),

# ================= BABYSITTING =================
(r"\b(babysitter|child care)\b","babysitting service"),

# ================= INTERNATIONAL MOVING =================
(r"\b(international moving)\b","international movers"),

# ================= RENTALS =================
(r"\b(rent furniture|rent bike|rent car)\b","rental service"),

# ================= FACTORY / INDUSTRIAL =================
(r"\b(machine repair|industrial repair)\b","industrial service"),

# ================= TRANSLATION =================
(r"\b(translation|translator)\b","translation service"),

]


INTENT_SCHEMA = {
    "name": "intent_extraction",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "search_term": {"type": "string"},
            "description": {"type": "string"},
            "constraints": {"type": "array", "items": {"type": "string"}},
            "ask_city": {"type": "boolean"},
        },
        "required": ["search_term", "description", "constraints", "ask_city"],
    },
}

def should_use_llm(search_term: str, original: str) -> bool:
    o = (original or "").strip().lower()
    s = (search_term or "").strip().lower()
    if not s:
        return True
    if s == o:               # looks like we echoed the user's sentence
        return True
    if len(s.split()) > 6:   # too long for a clean service term
        return True
    return False

def llm_extract_intent(user_message: str) -> dict | None:
    # OpenAI quota is 0 right now, so disable LLM to avoid crashes
    return None



def _infer_search_term(user_text: str) -> str | None:
    t = (user_text or "").strip().lower()
    if not t:
        return None

    # ✅ always try rules first
    for pattern, term in _INTENT_RULES:
        if re.search(pattern, t):
            return term

    # short direct profession/service
    if len(t.split()) <= 6 and not re.search(r"\b(i have|i need|problem|issue|help me|looking for|repair|fix|service)\b", t):
        return user_text.strip()

    return "local service"



def _describe_problem(problem_text: str, search_term: str) -> str:
    info = _TERM_DESCRIPTIONS.get(search_term.lower())

    if info:
        return (
            f"📝 I understand: “{problem_text}”.\n"
            f"✅ You likely need **{search_term.title()}**.\n"
            f"ℹ️ {info}\n\n"
            f"📍 Tell me your city and I’ll show real nearby options with address, rating, and contact (when available)."
        )

    # fallback if search_term not in dictionary
    return (
        f"📝 I understand: “{problem_text}”.\n"
        f"✅ I’ll look for **{search_term.title()}** near you.\n\n"
        f"📍 Tell me your city and I’ll show real options with address, rating, and contact (when available)."
    )


@app.post("/chat")
def chat(payload: dict):
    chat_id = (payload.get("chatId") or payload.get("chat_id") or "").strip()
    message = (payload.get("message") or "").strip()

    if not chat_id:
        raise HTTPException(status_code=400, detail="chatId is required.")
    if not message:
        return {"reply": "Please type your problem or the service you need."}

    state = _sessions.get(chat_id, {})

    # -------------------------
    # STEP 2: waiting for city
    # -------------------------
    if state.get("awaiting_city"):
        city = message
        search_term = state.get("search_term") or "professionals"
        problem_text = state.get("problem_text") or search_term

        constraints = state.get("constraints") or []
        query_term = f"{' '.join(constraints)} {search_term}".strip()

        people = find_people(query_term, city)

        # clear session
        _sessions.pop(chat_id, None)

        return {
            "reply": f"Here are **{search_term.title()}** near **{city}** (based on: “{problem_text}”):",
            "results": people
        }

    # -------------------------
    # STEP 1: infer what to search + ask city
    # -------------------------
    search_term = _infer_search_term(message)

    intent = None
    if should_use_llm(search_term, message):
        intent = llm_extract_intent(message)

    constraints = []
    ai_desc = ""

    if intent and intent.get("search_term"):
        search_term = intent["search_term"].strip()
        constraints = intent.get("constraints") or []
        ai_desc = (intent.get("description") or "").strip()

    if not search_term:
        return {"reply": "Tell me what you need (for example: plumber, lawyer, CA, web developer) and I’ll ask your city."}

    _sessions[chat_id] = {
        "awaiting_city": True,
        "problem_text": message,
        "search_term": search_term,
        "constraints": constraints,
        "ai_desc": ai_desc,
    }

    desc = ai_desc or _describe_problem(message, search_term)
    return {"reply": desc + "\n\nWhich city are you in?"}
