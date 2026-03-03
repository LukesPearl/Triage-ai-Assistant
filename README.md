Triage AI Assistant
Project Goal

To improve accessibility to healthcare by providing AI-powered symptom triage that routes patients to appropriate facilities, reducing unnecessary hospital congestion.

Hypothesis

If patients receive AI-based preliminary triage guidance, then:

Non-emergency cases will avoid overcrowded emergency rooms.

Patients will access appropriate facilities faster.

Healthcare system congestion will decrease.

How It Works

User describes symptoms (English or Swahili).

AI classifies condition into:

Infectious

Deficiency

Hereditary

Emergency

System calculates probability scores.

Assigns risk level.

Recommends facility + timing guidance.

Validation

System performance measured using:

True Positive (TP)

True Negative (TN)

False Positive (FP)

False Negative (FN)

Macro-averaged accuracy

10 simulated clinical trials

Architecture

Mobile UI → FastAPI Backend → Triage Engine → Risk + Routing Output
