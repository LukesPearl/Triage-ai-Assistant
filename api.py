from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from triage_engine import predict

app = FastAPI(title="Triage AI API")

# ✅ Allow frontend apps (like Base44) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all domains (safe for demo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Req(BaseModel):
    text: str
    lang: str = "en"

@app.post("/triage")
def triage(req: Req):
    p = predict(req.text)

    return {
        "category": p.decision,
        "facility": p.facility,
        "urgency": p.urgency,
        "best_time": p.best_time,
        "actions": p.actions,
        "scores": p.scores,
        "matched": p.matched,
        "note": p.note,
    }
