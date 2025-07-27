import streamlit as st
from google import genai
from google.genai import types
import json
import asyncio
import time

# ─── CONFIG ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="📘 SmartPrep AI Tutor",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4f46e5;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        color: #6b7280;
        font-size: 1.1rem;
    }
    
    .setup-container {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .quiz-container {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .question-counter {
        color: #4f46e5;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .question-text {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    
    .feedback-container {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid #4f46e5;
        margin-top: 1rem;
    }
    
    .feedback-title {
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.75rem;
        color: #1f2937;
    }
    
    .explanation-text {
        color: #4b5563;
        line-height: 1.6;
    }
    
    .results-container {
        background: white;
        padding: 3rem 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .final-score {
        font-size: 3rem;
        font-weight: 700;
        color: #4f46e5;
        margin: 1rem 0;
    }
    
    .progress-container {
        margin-bottom: 1.5rem;
    }
    
    .stButton > button {
        width: 100%;
        background: #4f46e5;
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #4338ca;
        transform: translateY(-1px);
    }
    
    .stRadio > div {
        gap: 0.75rem;
    }
    
    .stRadio > div > label {
        background: white;
        border: 2px solid #d1d5db;
        border-radius: 0.5rem;
        padding: 1rem;
        cursor: pointer;
        transition: all 0.2s;
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    .stRadio > div > label:hover {
        border-color: #4f46e5;
        background: #f8fafc;
    }
    
    .stSelectbox > div > div {
        border-radius: 0.5rem;
        border: 2px solid #d1d5db;
    }
    
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .loading-dots {
        display: flex;
        gap: 0.25rem;
    }
    
    .loading-dot {
        width: 0.75rem;
        height: 0.75rem;
        background: #4f46e5;
        border-radius: 50%;
        animation: bounce 1.4s ease-in-out infinite both;
    }
    
    .loading-dot:nth-child(1) { animation-delay: -0.32s; }
    .loading-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    .success-message {
        background: #f0fdf4;
        border: 2px solid #22c55e;
        color: #15803d;
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        text-align: center;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #fef2f2;
        border: 2px solid #ef4444;
        color: #dc2626;
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load your secure API key
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Please configure your GEMINI_API_KEY in Streamlit secrets.")
    st.stop()

# ─── GENERATION HELPERS ──────────────────────────────────────────────────────────
def call_gemini_structured(subject, difficulty):
    """Generate a structured question using Gemini API with JSON schema"""
    prompt = f"""Create one multiple-choice WAEC/UTME question for the subject "{subject}" at a "{difficulty}" difficulty level. 
    The question should be unique and academically rigorous. Ensure the options are plausible and the explanation is clear and educational."""
    
    # Define the JSON schema for structured output
    schema = {
        "type": "object",
        "properties": {
            "question": {"type": "string"},
            "options": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 4,
                "maxItems": 4
            },
            "answer": {"type": "string"},
            "explanation": {"type": "string"}
        },
        "required": ["question", "options", "answer", "explanation"]
    }
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": schema
            }
        )
        
        result = json.loads(response.candidates[0].content.parts[0].text)
        
        # Validate that the answer is one of the options
        if result["answer"] not in result["options"]:
            result["answer"] = result["options"][0]  # Fallback to first option
            
        return result
        
    except Exception as e:
        st.error(f"Error generating question: {str(e)}")
        return None

def preload_questions(subject, difficulty, count=3):
    """Preload multiple questions for smooth user experience"""
    questions = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(count):
        status_text.text(f"Generating question {i+1} of {count}...")
        progress_bar.progress((i) / count)
        
        question = call_gemini_structured(subject, difficulty)
        if question:
            questions.append(question)
            
    progress_bar.progress(1.0)
    status_text.text("Questions ready!")
    time.sleep(0.5)  # Brief pause to show completion
    progress_bar.empty()
    status_text.empty()
    
    return questions

# ─── SESSION STATE SETUP ─────────────────────────────────────────────────────────
if "quiz_state" not in st.session_state:
    st.session_state.quiz_state = {
        "stage": "setup",  # setup, quiz, results
        "subject": None,
        "difficulty": None,
        "questions": [],
        "current_index": 0,
        "score": 0,
        "user_answers": [],
        "show_feedback": False,
        "quiz_length": 10
    }

quiz = st.session_state.quiz_state

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1 class="main-title">📘 SmartPrep AI Tutor</h1>
    <p class="main-subtitle">Your AI-powered guide for WAEC/UTME success</p>
</div>
""", unsafe_allow_html=True)

# ─── SETUP SCREEN ────────────────────────────────────────────────────────────────
if quiz["stage"] == "setup":
    st.markdown('<div class="setup-container">', unsafe_allow_html=True)
    st.markdown("### Let's Get Started!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.selectbox(
            "Subject",
            ["Mathematics", "Biology", "English Language", "Physics", "Chemistry", "Government"],
            key="subject_select"
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty Level",
            ["Easy", "Medium", "Hard"],
            index=1,  # Default to Medium
            key="difficulty_select"
        )
    
    if st.button("Start Quiz", key="start_quiz"):
        quiz["subject"] = subject
        quiz["difficulty"] = difficulty
        quiz["stage"] = "loading"
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ─── LOADING SCREEN ───────────────────────────────────────────────────────────────
elif quiz["stage"] == "loading":
    st.markdown("""
    <div class="loading-spinner">
        <div class="loading-dots">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='text-align: center; margin-top: 1rem;'>Preparing {quiz['subject']} questions...</p>", unsafe_allow_html=True)
    
    # Generate initial batch of questions
    questions = preload_questions(quiz["subject"], quiz["difficulty"], 5)
    
    if questions:
        quiz["questions"] = questions
        quiz["stage"] = "quiz"
        st.rerun()
    else:
        st.error("Failed to generate questions. Please try again.")
        quiz["stage"] = "setup"
        st.rerun()

# ─── QUIZ SCREEN ──────────────────────────────────────────────────────────────────
elif quiz["stage"] == "quiz":
    # Progress bar
    progress = (quiz["current_index"]) / quiz["quiz_length"]
    st.progress(progress)
    
    # Current question
    current_q = quiz["questions"][quiz["current_index"]]
    
    st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
    
    # Question counter and text
    st.markdown(f'<p class="question-counter">Question {quiz["current_index"] + 1} of {quiz["quiz_length"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="question-text">{current_q["question"]}</div>', unsafe_allow_html=True)
    
    # Answer options
    if not quiz["show_feedback"]:
        user_choice = st.radio(
            "Select your answer:",
            current_q["options"],
            key=f"question_{quiz['current_index']}",
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Submit Answer", key="submit_answer"):
                quiz["user_answers"].append(user_choice)
                quiz["show_feedback"] = True
                
                # Check if answer is correct
                if user_choice == current_q["answer"]:
                    quiz["score"] += 1
                
                st.rerun()
    
    # Feedback section
    if quiz["show_feedback"]:
        user_answer = quiz["user_answers"][quiz["current_index"]]
        correct_answer = current_q["answer"]
        is_correct = user_answer == correct_answer
        
        # Show result
        if is_correct:
            st.markdown('<div class="success-message">✅ Correct! Well done.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-message">❌ Incorrect. The correct answer was: {correct_answer}</div>', unsafe_allow_html=True)
        
        # Show explanation
        st.markdown(f"""
        <div class="feedback-container">
            <div class="feedback-title">💡 Explanation</div>
            <div class="explanation-text">{current_q["explanation"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Next question button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if quiz["current_index"] + 1 >= quiz["quiz_length"]:
                if st.button("View Results", key="view_results"):
                    quiz["stage"] = "results"
                    st.rerun()
            else:
                if st.button("Next Question", key="next_question"):
                    quiz["current_index"] += 1
                    quiz["show_feedback"] = False
                    
                    # Generate more questions if needed
                    if len(quiz["questions"]) - quiz["current_index"] < 3:
                        with st.spinner("Loading more questions..."):
                            new_questions = preload_questions(quiz["subject"], quiz["difficulty"], 3)
                            quiz["questions"].extend(new_questions)
                    
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ─── RESULTS SCREEN ───────────────────────────────────────────────────────────────
elif quiz["stage"] == "results":
    st.balloons()
    
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    st.markdown("## 🎉 Quiz Complete!")
    st.markdown("Here's how you performed:")
    
    score_percentage = (quiz["score"] / quiz["quiz_length"]) * 100
    st.markdown(f'<div class="final-score">{quiz["score"]} / {quiz["quiz_length"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**{score_percentage:.1f}% Score**")
    
    # Performance feedback
    if score_percentage >= 80:
        st.markdown("🌟 **Excellent work!** You have a strong grasp of the material.")
    elif score_percentage >= 60:
        st.markdown("👍 **Good job!** Keep practicing to improve further.")
    else:
        st.markdown("📚 **Keep studying!** Review the explanations and try again.")
    
    if st.button("Take Another Quiz", key="restart_quiz"):
        # Reset quiz state
        st.session_state.quiz_state = {
            "stage": "setup",
            "subject": None,
            "difficulty": None,
            "questions": [],
            "current_index": 0,
            "score": 0,
            "user_answers": [],
            "show_feedback": False,
            "quiz_length": 10
        }
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ─── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; font-size: 0.9rem;'>"
    "Powered by Google Gemini AI • Built for Nigerian Students"
    "</div>", 
    unsafe_allow_html=True
)