import streamlit as st
from google import genai
from google.genai import types

# ─── CONFIG ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="📘 SmartPrep AI Tutor",
    layout="centered",
)

# Load your secure API key
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# ─── GENERATION HELPERS ──────────────────────────────────────────────────────────
def call_gemini(payload):
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=payload["contents"],
        generation_config=payload.get("generationConfig", {})
    )
    return resp

def generate_question(subject, difficulty):
    prompt = (
        f"Create one multiple-choice WAEC/UTME question for '{subject}' "
        f"at '{difficulty}' difficulty. Label options A), B), C), D), then:"
        "\nAnswer: [e.g., C]\nExplanation: [detail]"
    )
    payload = {"contents":[{"role":"user","parts":[{"text":prompt}]}]}
    data = call_gemini(payload)
    text = data.candidates[0].content.parts[0].text.strip().split("\n")
    # parse into question/options/answer/expl …
    # (same parsing logic you already have)
    return parsed_question

def generate_followup(prompt):
    payload = {"contents":[{"role":"user","parts":[{"text":prompt}]}]}
    data = call_gemini(payload)
    return data.candidates[0].content.parts[0].text.strip()

# ─── SESSION STATE SETUP ─────────────────────────────────────────────────────────
if "quiz" not in st.session_state:
    st.session_state.quiz = {
        "subject": None,
        "difficulty": None,
        "questions": [],
        "index": 0,
        "score": 0,
        "feedback": None,
        "hints": []
    }

quiz = st.session_state.quiz

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.title("📘 SmartPrep AI – WAEC/UTME Tutor")
st.markdown("> Your AI‑powered guide for exam success")

# ─── SETUP SCREEN ────────────────────────────────────────────────────────────────
if quiz["subject"] is None:
    with st.form("setup"):
        subject = st.selectbox("Subject", ["Mathematics","Biology","English","Physics","Chemistry","Government"])
        difficulty = st.selectbox("Difficulty", ["Easy","Medium","Hard"])
        start = st.form_submit_button("Start Quiz")
    if start:
        quiz.update({
            "subject": subject,
            "difficulty": difficulty,
            "questions": [generate_question(subject, difficulty) for _ in range(3)],  # preload 3
            "index": 0,
            "score": 0,
            "feedback": None,
            "hints": []
        })
        st.experimental_rerun()
else:
    # ─── QUIZ FLOW ────────────────────────────────────────────────────────────────
    q = quiz["questions"][quiz["index"]]
    
    st.progress((quiz["index"]) / 10)  # assuming 10‑question quiz
    st.subheader(f"{quiz['subject']} Question {quiz['index']+1}")
    st.write(q["question"])
    
    choice = st.radio("Pick an answer", q["options"], key=f"opt{quiz['index']}")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("Ask for Hint"):
            hint = generate_followup(f"Give a one-sentence hint (no answer) for: {q['question']}")
            quiz["hints"].append(hint)
    with col2:
        if st.button("Submit"):
            correct = (choice == q["answer"])
            if correct:
                st.success("✅ Correct!")
                quiz["score"] += 1
            else:
                st.error(f"❌ Wrong. Correct: {q['answer']}")
            quiz["feedback"] = q["explanation"]
    with col3:
        if quiz["feedback"] and st.button("Next"):
            # preload another if needed
            if len(quiz["questions"]) - quiz["index"] < 3:
                quiz["questions"].append(generate_question(quiz["subject"], quiz["difficulty"]))
            quiz["index"] += 1
            quiz["feedback"] = None
            st.experimental_rerun()
    
    # show hint(s) & feedback
    if quiz["hints"]:
        st.info("💡 Hint: " + quiz["hints"][-1])
    if quiz["feedback"]:
        st.markdown(f"**Explanation:** {quiz['feedback']}")

    # ─── COMPLETION SCREEN ────────────────────────────────────────────────────────
    if quiz["index"] >= 10:
        st.balloons()
        st.success(f"🎉 You scored {quiz['score']}/10!")
        if st.button("Restart Quiz"):
            for k in quiz:
                quiz[k] = None if k in ("subject","difficulty") else []
            st.experimental_rerun()
