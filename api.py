from fastapi import FastAPI
from pydantic import BaseModel
from triage_engine import predict

app = FastAPI(title="Triage AI API")

class Req(BaseModel):
    text: str
    lang: str = "en"

@app.post("/triage")
def triage(req: Req):
    p = predict(req.text, language=req.lang)
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
