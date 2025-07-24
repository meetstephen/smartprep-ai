import streamlit as st
from google import genai
from google.genai import types

# Page setup
st.title("📘 SmartPrep AI – WAEC/UTME Tutor")
st.write("Welcome to your AI-powered exam preparation tutor!")

# Load Gemini API key securely
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def generate_question(subject):
    # Prompt with structure enforced by system_instruction
    prompt = f"Create one multiple choice {subject} question."
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=(
                "Provide output in this exact format:\n"
                "Question: ...\n"
                "A) ...\n"
                "B) ...\n"
                "C) ...\n"
                "D) ...\n"
                "Answer: <single letter>\n"
                "Explanation: <detailed explanation>"
            )
        )
    )
    text = resp.text or ""
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Parse structured content
    question = next((l.split(":",1)[1].strip() for l in lines if l.startswith("Question:")), "")
    options = [l for l in lines if l[:2] in ("A)", "B)", "C)", "D)")]
    if len(options) < 4:
        options += ["(Option missing)"] * (4 - len(options))
    answer_letter = next((l.split(":",1)[1].strip() for l in lines if l.startswith("Answer:")), "")
    answer = next((opt for opt in options if opt.startswith(answer_letter)), answer_letter)

    explanation_lines = [l.split(":",1)[1].strip() for l in lines if l.startswith("Explanation:")]
    explanation_index = lines.index(next((l for l in lines if l.startswith("Explanation:")), lines[-1]))
    explanation = " ".join(lines[explanation_index:]) if explanation_lines else "No explanation provided."

    return {
        "subject": subject,
        "question": question or "No question generated.",
        "options": options,
        "answer": answer,
        "explanation": explanation
    }

# Subject selector
subject = st.selectbox("Choose a subject:", ["Mathematics", "Biology", "English"])
if st.session_state.get("quiz_subject") != subject:
    st.session_state.quiz_subject = subject
    st.session_state.quiz_data = [generate_question(subject)]
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.feedback = None

# Quiz interface
if st.session_state.index < len(st.session_state.quiz_data):
    q = st.session_state.quiz_data[st.session_state.index]
    st.subheader(f"{q['subject']} Question {st.session_state.index + 1}:")
    st.write(q["question"])  # ✅ Displays the question
    choice = st.radio("Pick an answer:", q["options"])

    if st.button("Submit"):
        if choice == q["answer"]:
            st.success("Correct! ✅")
            st.session_state.score += 1
        else:
            st.error(f"Wrong! Correct: {q['answer']}")
        st.session_state.feedback = q["explanation"]

    if st.session_state.feedback:
        st.write("💡 Explanation:", st.session_state.feedback)
        if st.button("Next Question"):
            st.session_state.quiz_data.append(generate_question(subject))
            st.session_state.index += 1
            st.session_state.feedback = None
            st.rerun()
else:
    st.success(f"🎉 Quiz Complete! Score: {st.session_state.score}/{len(st.session_state.quiz_data)}")
    if st.button("Restart"):
        st.session_state.quiz_data = [generate_question(subject)]
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.feedback = None
        st.rerun()
