import streamlit as st
from triage_engine import predict, FACILITY

st.set_page_config(page_title="Triage AI Assistant", page_icon="🩺", layout="centered")

# ---------------------------
# Readable modern theme
# ---------------------------
st.markdown("""
<style>
html, body, [class*="st-"], .stApp, .stMarkdown { color:#0B1220 !important; }
.stApp { background: linear-gradient(180deg, #F5FBFF 0%, #F0FFF7 100%); }
.card {
  background: rgba(255,255,255,0.97);
  border: 1px solid rgba(11,18,32,0.08);
  border-radius: 18px;
  padding: 16px;
  box-shadow: 0 10px 22px rgba(11,18,32,0.05);
  margin-bottom: 12px;
}
.h1 { font-size: 30px; font-weight: 800; letter-spacing: -0.5px; margin: 0; }
.sub { color: rgba(11,18,32,0.70) !important; margin-top: 6px; font-size: 14px; }
.pill {
  display:inline-block; padding:6px 10px; border-radius:999px;
  background: rgba(44,125,160,0.12); color:#145A73 !important;
  font-weight:700; font-size:12px; margin-right:6px;
}
.emergency button {
  background:#F4A261 !important; color:#111 !important;
  border-radius:14px !important; border:0 !important; font-weight:800 !important;
}
.footer { color: rgba(11,18,32,0.60) !important; font-size: 12px; margin-top: 14px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Language strings
# ---------------------------
lang = st.sidebar.selectbox("Language / Lugha", ["English", "Swahili"])
lk = "en" if lang == "English" else "sw"

TEXT = {
    "en": {
        "title": "Triage AI Assistant",
        "tagline": "Chat normally, then I route symptoms to the right care. (Educational demo — not a diagnosis.)",
        "hello": "Hi 🙂 Talk to me normally. If you describe symptoms, I’ll classify them and recommend the right care.",
        "privacy": "Privacy: Inputs are not stored. Runs locally on your computer.",
        "type_here": "Type a message… (English / Swahili / a bit of Sheng)",
        "logic": "How I decided (for judges)",
        "testing": "Testing & Validation",
        "run_tests": "Run 10 trials",
        "success": "Success Criteria Check",
        "acc": "Accuracy",
        "cat_rate": "Correct categorisation rate",
        "fac_rate": "Correct facility recommendation rate",
        "threshold": "Pass threshold (e.g., 0.80 = 80%)",
        "course": "Course of action",
        "timing": "Timing guidance",
    },
    "sw": {
        "title": "Msaidizi wa Triage wa AI",
        "tagline": "Ongea kawaida, kisha nitakuonyesha huduma sahihi. (Mfano wa kielimu — si utambuzi.)",
        "hello": "Habari 🙂 Ongea nami kawaida. Ukieleza dalili, nitaziweka kwenye makundi na kukuonyesha mahali pa kwenda.",
        "privacy": "Faragha: Maandishi hayahifadhiwi. Inaendeshwa kwenye kompyuta yako.",
        "type_here": "Andika ujumbe… (Kiingereza / Kiswahili / Sheng kidogo)",
        "logic": "Jinsi nilivyoamua (kwa majaji)",
        "testing": "Upimaji & Uhakiki",
        "run_tests": "Endesha majaribio 10",
        "success": "Kigezo cha Mafanikio",
        "acc": "Usahihi",
        "cat_rate": "Kiwango cha kuweka kundi sahihi",
        "fac_rate": "Kiwango cha mahali sahihi",
        "threshold": "Kizingiti cha kupita (mf: 0.80 = 80%)",
        "course": "Hatua za kuchukua",
        "timing": "Mwongozo wa muda",
    }
}[lk]

# ---------------------------
# Header
# ---------------------------
st.markdown(f"""
<div class="card">
  <div class="h1">{TEXT["title"]}</div>
  <div class="sub">{TEXT["tagline"]}</div>
</div>
""", unsafe_allow_html=True)

st.caption("📝 Disclaimer: This is an educational triage demo, not medical advice. If you feel unsafe, seek emergency care.")

# ---------------------------
# Chat state
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": TEXT["hello"]}]

# ---------------------------
# Trials (10 simulated trials)
# ---------------------------
TRIALS_10 = [
    ("I have fever and cough and chills", "INFECTIOUS", FACILITY["INFECTIOUS"]),
    ("Runny nose and cough, feel hot", "INFECTIOUS", FACILITY["INFECTIOUS"]),
    ("Vomiting and diarrhea with fever", "INFECTIOUS", FACILITY["INFECTIOUS"]),
    ("Nina homa na kikohozi", "INFECTIOUS", FACILITY["INFECTIOUS"]),
    ("I feel dizzy and pale and tired", "DEFICIENCY", FACILITY["DEFICIENCY"]),
    ("Niko na kizunguzungu na uchovu", "DEFICIENCY", FACILITY["DEFICIENCY"]),
    ("Weak and fatigue, nearly fainting", "DEFICIENCY", FACILITY["DEFICIENCY"]),
    ("I bruise easily and have joint pain", "HEREDITARY", FACILITY["HEREDITARY"]),
    ("Unexplained bleeding and family history", "HEREDITARY", FACILITY["HEREDITARY"]),
    ("Severe bleeding", "EMERGENCY", FACILITY["EMERGENCY"]),
]

CLASSES = ["INFECTIOUS", "DEFICIENCY", "HEREDITARY", "UNCLEAR", "EMERGENCY"]

def confusion_counts_one_vs_rest(y_true, y_pred, positive_label):
    TP = TN = FP = FN = 0
    for t, p in zip(y_true, y_pred):
        t_pos = (t == positive_label)
        p_pos = (p == positive_label)
        if t_pos and p_pos:
            TP += 1
        elif (not t_pos) and (not p_pos):
            TN += 1
        elif (not t_pos) and p_pos:
            FP += 1
        elif t_pos and (not p_pos):
            FN += 1
    return TP, TN, FP, FN

def accuracy_from_counts(TP, TN, FP, FN):
    denom = TP + TN + FP + FN
    return (TP + TN) / denom if denom else 0.0

# ---------------------------
# Tabs
# ---------------------------
tab_chat, tab_test = st.tabs(["Chat", TEXT["testing"]])

with tab_chat:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    user_msg = st.chat_input(TEXT["type_here"])
    if user_msg:
        st.session_state.messages.append({"role": "user", "content": user_msg})
        with st.chat_message("user"):
            st.markdown(user_msg)

        pred = predict(user_msg, language=lk)

        reply = (
            f"**Diagnosis & Routing**\n\n"
            f"**Category:** {pred.decision}\n\n"
            f"**Recommended location:** {pred.facility}\n\n"
            f"**{TEXT['timing']}:** {pred.urgency} | Best time: {pred.best_time}\n\n"
            f"**{TEXT['course']}:**\n- " + "\n- ".join(pred.actions)
        )

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

        with st.expander(TEXT["logic"]):
            st.write("Decision:", pred.decision)
            st.write("Facility:", pred.facility)
            st.write("Urgency:", pred.urgency)
            st.write("Best time:", pred.best_time)
            st.write("Scores:", pred.scores)
            st.write("Matched keywords:", pred.matched)
            st.write("Note:", pred.note)

    st.markdown(f"<div class='footer'>{TEXT['privacy']}</div>", unsafe_allow_html=True)

with tab_test:
    st.markdown(f"""
    <div class="card">
      <div class="h1">{TEXT["testing"]}</div>
      <div class="sub">10 simulated trials → compare predicted category + facility against expected routing.</div>
    </div>
    """, unsafe_allow_html=True)

    threshold = st.slider(TEXT["threshold"], 0.50, 1.00, 0.80, 0.05)

    if st.button(TEXT["run_tests"], use_container_width=True):
        y_true, y_pred = [], []
        rows = []

        for text, exp_cat, exp_fac in TRIALS_10:
            pred = predict(text, language=lk)
            y_true.append(exp_cat)
            y_pred.append(pred.decision)

            rows.append({
                "Input": text,
                "Expected Category": exp_cat,
                "Predicted Category": pred.decision,
                "Expected Facility": exp_fac,
                "Predicted Facility": pred.facility,
                "Category Correct?": exp_cat == pred.decision,
                "Facility Correct?": exp_fac == pred.facility,
            })

        total = len(rows)
        cat_correct = sum(r["Category Correct?"] for r in rows)
        fac_correct = sum(r["Facility Correct?"] for r in rows)
        categorisation_rate = cat_correct / total
        facility_rate = fac_correct / total

        per_class = []
        for cls in CLASSES:
            TP, TN, FP, FN = confusion_counts_one_vs_rest(y_true, y_pred, cls)
            acc = accuracy_from_counts(TP, TN, FP, FN)
            per_class.append({"Class": cls, "TP": TP, "TN": TN, "FP": FP, "FN": FN, "Accuracy": round(acc, 3)})

        macro_accuracy = sum(p["Accuracy"] for p in per_class) / len(per_class)

        st.markdown(f"""
        <div class="card">
          <span class="pill">{TEXT["success"]}</span><br><br>
          <b>{TEXT["acc"]} (macro, TP/TN/FP/FN):</b> {macro_accuracy:.2%}<br>
          <b>{TEXT["cat_rate"]}:</b> {categorisation_rate:.2%}<br>
          <b>{TEXT["fac_rate"]}:</b> {facility_rate:.2%}<br><br>
          <b>PASS?</b><br>
          • Accuracy ≥ {threshold:.0%}: {"✅" if macro_accuracy >= threshold else "❌"}<br>
          • Categorisation ≥ {threshold:.0%}: {"✅" if categorisation_rate >= threshold else "❌"}<br>
          • Facility ≥ {threshold:.0%}: {"✅" if facility_rate >= threshold else "❌"}
        </div>
        """, unsafe_allow_html=True)

        st.write("Trial results:")
        st.dataframe(rows, use_container_width=True)

        st.write("TP/TN/FP/FN and Accuracy per class (one-vs-rest):")
        st.dataframe(per_class, use_container_width=True)

        st.caption("TP/TN/FP/FN is binary; for 3+ categories we compute one-vs-rest per class so the formula still applies.")