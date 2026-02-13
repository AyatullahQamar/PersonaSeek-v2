import re, time
from typing import List, Tuple, Dict
from intent_db import init_db, connect

CACHE_TTL = 60  # seconds

_cache = {
    "loaded_at": 0.0,
    "rules": [],          # List[(compiled_regex, search_term)]
    "descs": {}           # Dict[search_term_lower, description]
}

def refresh(force: bool = False):
    now = time.time()
    if not force and (now - _cache["loaded_at"] < CACHE_TTL):
        return

    init_db()

    with connect() as conn:
        rows = conn.execute("""
            SELECT pattern, search_term
            FROM intent_rules
            WHERE enabled = 1
            ORDER BY priority ASC, id ASC
        """).fetchall()

        compiled: List[Tuple[re.Pattern, str]] = []
        for r in rows:
            try:
                compiled.append((re.compile(r["pattern"], re.IGNORECASE), r["search_term"]))
            except re.error:
                # invalid regex in DB should not crash server
                continue

        drows = conn.execute("""
            SELECT search_term, description
            FROM intent_descriptions
        """).fetchall()

        descs: Dict[str, str] = {d["search_term"].lower(): d["description"] for d in drows}

    _cache["rules"] = compiled
    _cache["descs"] = descs
    _cache["loaded_at"] = now

def match_search_term(text: str) -> str | None:
    refresh()
    t = (text or "").strip()
    if not t:
        return None

    for rx, term in _cache["rules"]:
        if rx.search(t):
            return term
    return None

def get_description(search_term: str) -> str | None:
    refresh()
    return _cache["descs"].get((search_term or "").lower())
