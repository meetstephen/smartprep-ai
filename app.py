import streamlit as st
from google import genai
from google.genai import types
import json
import time
import asyncio

# ─── PAGE CONFIGURATION ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="📘 SmartPrep AI Tutor",
    layout="centered"
)

# ─── SIMPLIFIED STYLING ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .quiz-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
    .success-msg {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        text-align: center;
    }
    .error-msg {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ─── API CLIENT SETUP WITH ERROR HANDLING ───────────────────────────────────────
@st.cache_resource
def initialize_client():
    """Initialize the Gemini client with proper error handling"""
    try:
        from google import genai
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            st.error("❌ GEMINI_API_KEY not found in secrets. Please add it in your Streamlit app settings.")
            st.stop()
        
        client = genai.Client(api_key=api_key)
        # Test the connection with a simple call
        test_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [{"text": "Say 'API working'"}]}]
        )
        return client
    except ImportError:
        st.error("❌ Google GenAI library not installed. Please add 'google-genai' to requirements.txt")
        st.stop()
    except Exception as e:
        st.error(f"❌ API Connection Failed: {str(e)}")
        st.error("Please check your API key and internet connection.")
        st.stop()

# ─── SIMPLIFIED QUESTION GENERATION ─────────────────────────────────────────────
def generate_simple_question(client, subject, difficulty):
    """Generate a single question with basic error handling"""
    try:
        prompt = f"""
        Create a {difficulty.lower()} level multiple choice question for {subject}.
        
        Format your response EXACTLY like this example:
        Question: What is 2 + 2?
        A) 3
        B) 4
        C) 5
        D) 6
        Answer: B
        Explanation: 2 + 2 equals 4, which is option B.
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [{"text": prompt}]}]
        )
        
        content = response.candidates[0].content.parts[0].text.strip()
        return parse_question_response(content)
        
    except Exception as e:
        st.error(f"Question generation failed: {str(e)}")
        return None

def parse_question_response(content):
    """Parse the AI response into structured question data"""
    try:
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        question = ""
        options = []
        answer = ""
        explanation = ""
        
        for line in lines:
            if line.startswith("Question:"):
                question = line.replace("Question:", "").strip()
            elif line.startswith(("A)", "B)", "C)", "D)")):
                options.append(line)
            elif line.startswith("Answer:"):
                answer = line.replace("Answer:", "").strip()
            elif line.startswith("Explanation:"):
                explanation = line.replace("Explanation:", "").strip()
        
        if not all([question, len(options) >= 4, answer, explanation]):
            raise ValueError("Incomplete question data")
            
        return {
            "question": question,
            "options": options,
            "answer": answer,
            "explanation": explanation
        }
    except Exception:
        return None

# ─── SESSION STATE INITIALIZATION ───────────────────────────────────────────────
def initialize_session_state():
    """Initialize session state with default values"""
    if "app_stage" not in st.session_state:
        st.session_state.app_stage = "setup"
    if "subject" not in st.session_state:
        st.session_state.subject = "Mathematics"
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "Medium"
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False
    if "user_choice" not in st.session_state:
        st.session_state.user_choice = None

# ─── MAIN APPLICATION ───────────────────────────────────────────────────────────
def main():
    # Initialize session state
    initialize_session_state()
    
    # Initialize API client
    client = initialize_client()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: #4f46e5; font-size: 2.5rem;">📘 SmartPrep AI Tutor</h1>
        <p style="color: #6b7280;">Your AI-powered guide for WAEC/UTME success</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main application flow
    if st.session_state.app_stage == "setup":
        show_setup_screen(client)
    elif st.session_state.app_stage == "quiz":
        show_quiz_screen(client)
    elif st.session_state.app_stage == "results":
        show_results_screen()

def show_setup_screen(client):
    """Display the setup screen for subject and difficulty selection"""
    st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
    st.subheader("Let's Get Started!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.selectbox(
            "Select Subject:",
            ["Mathematics", "Biology", "English Language", "Physics", "Chemistry", "Government"],
            index=0
        )
    
    with col2:
        difficulty = st.selectbox(
            "Select Difficulty:",
            ["Easy", "Medium", "Hard"],
            index=1
        )
    
    if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
        with st.spinner("Generating your first question..."):
            # Update session state
            st.session_state.subject = subject
            st.session_state.difficulty = difficulty
            
            # Generate first question
            question = generate_simple_question(client, subject, difficulty)
            
            if question:
                st.session_state.current_question = question
                st.session_state.app_stage = "quiz"
                st.session_state.question_count = 1
                st.success("✅ Question generated successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Failed to generate question. Please try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_quiz_screen(client):
    """Display the quiz screen with current question"""
    if not st.session_state.current_question:
        st.error("No question available. Returning to setup...")
        st.session_state.app_stage = "setup"
        st.rerun()
        return
    
    question = st.session_state.current_question
    
    # Progress indicator
    st.progress(st.session_state.question_count / 10)
    
    st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
    
    # Question header
    st.markdown(f"**Question {st.session_state.question_count} of 10** - {st.session_state.subject}")
    st.markdown("---")
    
    # Question text
    st.markdown(f"### {question['question']}")
    
    # Answer options (only show if answer not revealed)
    if not st.session_state.show_answer:
        choice = st.radio(
            "Select your answer:",
            question['options'],
            key=f"q_{st.session_state.question_count}"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Submit Answer", type="primary", use_container_width=True):
                st.session_state.user_choice = choice
                st.session_state.show_answer = True
                
                # Check if correct
                if choice.startswith(question['answer']):
                    st.session_state.score += 1
                
                st.rerun()
    
    # Show feedback if answer submitted
    if st.session_state.show_answer:
        user_answer = st.session_state.user_choice
        correct_answer = question['answer']
        
        # Show result
        if user_answer.startswith(correct_answer):
            st.markdown('<div class="success-msg">✅ Correct! Well done.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-msg">❌ Incorrect. The correct answer was {correct_answer}.</div>', unsafe_allow_html=True)
        
        # Show explanation
        st.markdown("**💡 Explanation:**")
        st.info(question['explanation'])
        
        # Next question or finish
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.session_state.question_count >= 10:
                if st.button("View Results", type="primary", use_container_width=True):
                    st.session_state.app_stage = "results"
                    st.rerun()
            else:
                if st.button("Next Question", type="primary", use_container_width=True):
                    with st.spinner("Generating next question..."):
                        next_question = generate_simple_question(client, st.session_state.subject, st.session_state.difficulty)
                        
                        if next_question:
                            st.session_state.current_question = next_question
                            st.session_state.question_count += 1
                            st.session_state.show_answer = False
                            st.session_state.user_choice = None
                            st.rerun()
                        else:
                            st.error("Failed to generate next question. Please try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_results_screen():
    """Display the final results screen"""
    st.balloons()
    
    st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
    
    st.markdown("## 🎉 Quiz Complete!")
    st.markdown("---")
    
    # Score display
    score_percentage = (st.session_state.score / 10) * 100
    st.markdown(f"### Your Score: {st.session_state.score} / 10 ({score_percentage:.0f}%)")
    
    # Performance feedback
    if score_percentage >= 80:
        st.success("🌟 Excellent work! You have mastered this topic.")
    elif score_percentage >= 60:
        st.info("👍 Good job! Keep practicing to improve further.")
    else:
        st.warning("📚 Keep studying! Review the explanations and try again.")
    
    # Restart option
    if st.button("Take Another Quiz", type="primary", use_container_width=True):
        # Reset all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ─── RUN APPLICATION ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
