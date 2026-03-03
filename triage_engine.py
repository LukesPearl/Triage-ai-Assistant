import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

# ----------------------------
# TEXT HELPERS
# ----------------------------

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text

def apply_synonyms(text: str) -> str:
    """
    Offline language bridge (English + Swahili + a bit of Sheng)
    Maps common Swahili/Sheng symptom words into English keywords used by scoring.
    """
    t = normalize(text)

    replacements = {
        # Infectious
        "homa": "fever",
        "joto": "hot",
        "baridi": "chills",
        "mafua": "runny nose",
        "kikohozi": "cough",
        "koo inauma": "sore throat",
        "koo": "sore throat",
        "natapika": "vomiting",
        "kutapika": "vomiting",
        "kuhara": "diarrhea",
        "upele": "rash",

        # Deficiency
        "kizunguzungu": "dizzy",
        "mweupe": "pale",
        "uso mweupe": "pale",
        "uchovu": "fatigue",
        "nimechoka": "tired",
        "dhaifu": "weak",
        "nazimia": "faint",
        "kuzimia": "faint",

        # Hereditary
        "damu": "bleeding",
        "natokwa na damu": "bleeding",
        "michubuko": "bruise",
        "michubuko kirahisi": "easy bruising",
        "maumivu ya viungo": "joint pain",
        "viungo vinauma": "joint pain",
        "historia ya familia": "family history",
        "ugonjwa wa kurithi": "family history",
    }

    for k, v in replacements.items():
        t = t.replace(k, v)

    return t

def score_keywords(text: str, weights: Dict[str, int]) -> Tuple[int, List[str]]:
    t = apply_synonyms(text)
    score = 0
    matched: List[str] = []
    for kw, w in weights.items():
        if kw in t:
            score += w
            matched.append(kw)
    matched.sort()
    return score, matched

# ----------------------------
# EMERGENCY SAFETY CHECK
# ----------------------------

EMERGENCY_FLAGS = [
    "chest pain",
    "difficulty breathing",
    "cannot breathe",
    "can't breathe",
    "severe bleeding",
    "unconscious",
    "seizure",
    "slurred speech",
]

# ----------------------------
# WEIGHTED KEYWORD MODEL (PRESENTATION-ALIGNED)
# ----------------------------

INFECTIOUS_WEIGHTS = {
    "fever": 3, "high fever": 4, "cough": 2, "contagious": 4, "chills": 3, "hot": 2,
    "sore throat": 2, "runny nose": 2, "vomiting": 2, "diarrhea": 2, "rash": 2,
}

DEFICIENCY_WEIGHTS = {
    "dizzy": 3, "dizziness": 3, "pale": 3, "tired": 2, "fatigue": 3,
    "weak": 2, "faint": 3, "hair loss": 2, "craving ice": 4,
}

HEREDITARY_WEIGHTS = {
    "unexplained bleeding": 5, "bleeding": 3, "easy bruising": 4, "bruise": 3,
    "joint pain": 3, "clot": 4, "family history": 4, "blood disorder": 5,
}

# ----------------------------
# FACILITY ROUTING (FROM YOUR PRESENTATION)
# ----------------------------

FACILITY = {
    "INFECTIOUS": "City Urgent Care (Isolation Wing)",
    "DEFICIENCY": "Community Pharmacy & Nutrition Center",
    "HEREDITARY": "University Research Hospital (Hematology Dept)",
    "UNCLEAR": "Primary Care Physician",
    "EMERGENCY": "Nearest Emergency Room Immediately",
}

# ----------------------------
# TIMING + COURSE OF ACTION
# ----------------------------

GUIDANCE = {
    "INFECTIOUS": {
        "urgency": "Same day (today)",
        "best_time": "Early morning or late afternoon (often less crowded)",
        "actions_en": [
            "Limit close contact if you suspect contagious illness.",
            "Wear a mask if coughing/sneezing; wash hands regularly.",
            "Seek urgent care if symptoms worsen or fever is high/persistent."
        ],
        "actions_sw": [
            "Punguza mawasiliano ya karibu ikiwa unahisi ni ugonjwa wa kuambukiza.",
            "Vaa barakoa ikiwa unakohoa/una mafua; naosha mikono mara kwa mara.",
            "Tafuta huduma ya haraka ikiwa dalili zinaongezeka au homa ni kali/inaendelea."
        ],
    },
    "DEFICIENCY": {
        "urgency": "Within 1–3 days",
        "best_time": "Normal clinic hours (mid-morning tends to be calmer)",
        "actions_en": [
            "Consider a clinic test (e.g., hemoglobin/iron) if symptoms persist.",
            "Hydrate and eat balanced meals; seek care if fainting is frequent.",
        ],
        "actions_sw": [
            "Fikiria vipimo kliniki (mf: hemoglobini/chuma) ikiwa dalili zinaendelea.",
            "Kunywa maji na kula lishe bora; tafuta huduma ikiwa kuzimia ni mara kwa mara.",
        ],
    },
    "HEREDITARY": {
        "urgency": "Book an appointment (soon)",
        "best_time": "Weekday mornings are best for specialist reviews",
        "actions_en": [
            "Seek specialist evaluation and proper testing.",
            "If bleeding is heavy/sudden, treat as emergency and go to ER.",
        ],
        "actions_sw": [
            "Tafuta uchunguzi wa mtaalamu na vipimo sahihi.",
            "Ikiwa damu ni nyingi/ghafla, chukulia kama dharura na nenda ER.",
        ],
    },
    "UNCLEAR": {
        "urgency": "Within 24–72 hours",
        "best_time": "Any normal clinic time; go sooner if you feel worse",
        "actions_en": [
            "Visit a primary care clinic for assessment.",
            "If danger signs appear, seek urgent care/ER immediately.",
        ],
        "actions_sw": [
            "Nenda kliniki ya huduma ya msingi kwa uchunguzi.",
            "Dalili hatari zikionekana, tafuta huduma ya haraka/dharura mara moja.",
        ],
    },
    "EMERGENCY": {
        "urgency": "Immediately (now)",
        "best_time": "Go now",
        "actions_en": [
            "Seek emergency care immediately. Do not delay.",
            "Ask an adult for help or call emergency services if available.",
        ],
        "actions_sw": [
            "Tafuta huduma ya dharura sasa. Usichelewe.",
            "Omba msaada kwa mtu mzima au pigia huduma ya dharura ikiwezekana.",
        ],
    },
}

# ----------------------------
# OUTPUT STRUCTURE
# ----------------------------

@dataclass
class Prediction:
    decision: str
    facility: str
    urgency: str
    best_time: str
    actions: List[str]
    scores: Dict[str, int]
    matched: Dict[str, List[str]]
    note: str

def predict(text: str, language: str = "en") -> Prediction:
    t = apply_synonyms(text)

    # Emergency override
    if any(flag in t for flag in EMERGENCY_FLAGS):
        pack = GUIDANCE["EMERGENCY"]
        return Prediction(
            decision="EMERGENCY",
            facility=FACILITY["EMERGENCY"],
            urgency=pack["urgency"],
            best_time=pack["best_time"],
            actions=pack["actions_en"] if language == "en" else pack["actions_sw"],
            scores={"INFECTIOUS": 0, "DEFICIENCY": 0, "HEREDITARY": 0},
            matched={"INFECTIOUS": [], "DEFICIENCY": [], "HEREDITARY": []},
            note="Emergency red-flag detected (safety override)."
        )

    inf, inf_m = score_keywords(t, INFECTIOUS_WEIGHTS)
    defi, defi_m = score_keywords(t, DEFICIENCY_WEIGHTS)
    her, her_m = score_keywords(t, HEREDITARY_WEIGHTS)

    scores = {"INFECTIOUS": inf, "DEFICIENCY": defi, "HEREDITARY": her}
    matched = {"INFECTIOUS": inf_m, "DEFICIENCY": defi_m, "HEREDITARY": her_m}

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_cat, top_score = ranked[0]
    second_cat, second_score = ranked[1]

    # Unclear / tie / no signal
    if top_score == 0 or top_score == second_score:
        pack = GUIDANCE["UNCLEAR"]
        return Prediction(
            decision="UNCLEAR",
            facility=FACILITY["UNCLEAR"],
            urgency=pack["urgency"],
            best_time=pack["best_time"],
            actions=pack["actions_en"] if language == "en" else pack["actions_sw"],
            scores=scores,
            matched=matched,
            note="No strong signal or tie between categories."
        )

    pack = GUIDANCE[top_cat]
    return Prediction(
        decision=top_cat,
        facility=FACILITY[top_cat],
        urgency=pack["urgency"],
        best_time=pack["best_time"],
        actions=pack["actions_en"] if language == "en" else pack["actions_sw"],
        scores=scores,
        matched=matched,
        note="Highest weighted keyword score selected."
    )