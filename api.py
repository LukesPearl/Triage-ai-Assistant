from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from triage_engine import predict

app = FastAPI(title="Triage AI API")

# ✅ CORS: allow Base44 (and any frontend) to call your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # for school demo; later you can restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Req(BaseModel):
    text: str
    lang: str = "en"

@app.get("/")
def root():
    return {"status": "ok", "message": "Triage API is running"}

@app.post("/triage")
def triage(req: Req):
    p = predict(req.text, language=req.lang)
    return {
        "category": p.decision,
        "facility": getattr(p, "facility", None),
        "urgency": getattr(p, "urgency", None),
        "best_time": getattr(p, "best_time", None),
        "actions": getattr(p, "actions", None),
        "scores": p.scores,
        "matched": p.matched,
        "note": p.note,
    }
