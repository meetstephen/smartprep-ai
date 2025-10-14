import streamlit as st
from google import genai
import time
import random
from datetime import datetime, timedelta
import json
import hashlib
import base64
from io import BytesIO
import plotly.graph_objects as go
import plotly.express as px

# ─── PAGE CONFIGURATION ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="📘 SmartPrep AI Tutor - JAMB Edition",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── ENHANCED STYLING WITH MODERN DESIGN ─────────────────────────────────────────
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding-bottom: 2rem;
    }
    .block-container {
        padding-top: 2rem;
        max-width: 900px;
    }
    
    /* Card Styles */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
    }
    
    /* Header Styles */
    .main-header {
        text-align: center;
        margin-bottom: 3rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease;
    }
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.95;
        animation: fadeInUp 0.8s ease;
    }
    
    /* Navigation Bar */
    .nav-bar {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 1.25rem 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .nav-title {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .nav-stats {
        display: flex;
        gap: 1rem;
        font-size: 0.9rem;
        flex-wrap: wrap;
    }
    .nav-stat-item {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.4rem 0.9rem;
        border-radius: 20px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        transition: transform 0.2s ease;
    }
    .nav-stat-item:hover {
        transform: scale(1.05);
    }
    
    /* Quiz Container */
    .quiz-container {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        animation: fadeIn 0.5s ease;
    }
    
    /* Message Boxes */
    .success-msg {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        border-left: 5px solid #28a745;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.2);
        animation: slideInRight 0.5s ease;
    }
    .error-msg {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        border-left: 5px solid #dc3545;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(220, 53, 69, 0.2);
        animation: slideInRight 0.5s ease;
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 5px solid #ffc107;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(255, 193, 7, 0.2);
    }
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 5px solid #17a2b8;
        box-shadow: 0 4px 12px rgba(23, 162, 184, 0.2);
    }
    
    /* Timer Styles */
    .timer {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        color: #0d47a1;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(13, 71, 161, 0.2);
        border: 2px solid #2196f3;
    }
    .timer-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        border: 2px solid #ffc107;
        animation: pulse 1s infinite;
    }
    .timer-danger {
        background: linear-gradient(135deg, #f8d7da 0%, #fab1a0 100%);
        color: #721c24;
        border: 2px solid #dc3545;
        animation: pulse 0.5s infinite;
    }
    
    /* Badge Styles */
    .subject-badge {
        display: inline-block;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-right: 0.75rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 3px 10px rgba(79, 70, 229, 0.3);
        transition: transform 0.2s ease;
    }
    .subject-badge:hover {
        transform: scale(1.05);
    }
    
    /* Stats Card */
    .stats-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.75rem;
        border-radius: 15px;
        margin-bottom: 1.25rem;
        border-left: 5px solid #4f46e5;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease;
    }
    .stats-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
    }
    
    /* Achievement Card */
    .achievement-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.25rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border: 2px solid #e9ecef;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    .achievement-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
        border-color: #667eea;
    }
    .achievement-locked {
        filter: grayscale(1);
        opacity: 0.6;
    }
    .achievement-icon {
        font-size: 2.5rem;
        margin-right: 1.25rem;
        min-width: 3rem;
        text-align: center;
    }
    
    /* Level Badge */
    .level-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 800;
        width: 3.5rem;
        height: 3.5rem;
        line-height: 3.5rem;
        text-align: center;
        border-radius: 50%;
        font-size: 1.3rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        border: 3px solid white;
    }
    
    /* Progress Bars */
    .xp-bar {
        height: 1rem;
        background: #e9ecef;
        border-radius: 10px;
        margin-top: 0.75rem;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .xp-progress {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        transition: width 0.8s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
    }
    .mastery-bar {
        height: 0.7rem;
        background: #e9ecef;
        border-radius: 8px;
        margin: 0.75rem 0;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .mastery-progress {
        height: 100%;
        background: linear-gradient(90deg, #12b886 0%, #38d9a9 100%);
        border-radius: 8px;
        transition: width 0.8s ease;
        box-shadow: 0 2px 6px rgba(18, 184, 134, 0.4);
    }
    
    /* Progress Container */
    .progress-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border: 2px solid #e9ecef;
    }
    
    /* Streak Animation */
    .streak-flame {
        color: #ff9800;
        font-size: 1.75rem;
        animation: flicker 1.5s infinite alternate;
        display: inline-block;
    }
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { 
            opacity: 1; 
            transform: scale(1);
        }
        20%, 24%, 55% { 
            opacity: 0.7; 
            transform: scale(0.95);
        }
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes fadeInDown {
        from { 
            opacity: 0; 
            transform: translateY(-20px);
        }
        to { 
            opacity: 1; 
            transform: translateY(0);
        }
    }
    @keyframes fadeInUp {
        from { 
            opacity: 0; 
            transform: translateY(20px);
        }
        to { 
            opacity: 1; 
            transform: translateY(0);
        }
    }
    @keyframes slideInRight {
        from { 
            opacity: 0; 
            transform: translateX(30px);
        }
        to { 
            opacity: 1; 
            transform: translateX(0);
        }
    }
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.85; transform: scale(1.02); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    /* Button Styles */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* Radio Button Styles */
    .stRadio > label {
        font-weight: 600;
        color: #333;
    }
    .stRadio > div {
        gap: 0.5rem;
    }
    .stRadio > div > label {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .stRadio > div > label:hover {
        border-color: #667eea;
        background: #f8f9fa;
        transform: translateX(5px);
    }
    
    /* Selectbox Styles */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e9ecef;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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

# ─── EXPANDED JAMB SUBJECTS AND TOPICS ───────────────────────────────────────────
def get_jamb_subjects_and_topics():
    """Return a comprehensive dictionary of JAMB subjects and their topics"""
    return {
        "Mathematics": [
            "Algebra and Equations", "Geometry and Trigonometry", "Statistics and Probability",
            "Calculus", "Vectors", "Matrices", "Number Bases", "Sets and Logic"
        ],
        "Biology": [
            "Cell Biology", "Genetics", "Ecology", "Evolution", "Plant Biology", "Animal Biology",
            "Human Anatomy and Physiology", "Microbiology", "Reproduction", "Nutrition"
        ],
        "English Language": [
            "Comprehension", "Lexis and Structure", "Oral Forms", "Figurative Expressions",
            "Literary Devices", "Registers", "Synonyms and Antonyms", "Grammatical Structures"
        ],
        "Physics": [
            "Mechanics", "Energy", "Waves", "Optics", "Electricity and Magnetism", 
            "Modern Physics", "Heat and Temperature", "Electronics", "Nuclear Physics"
        ],
        "Chemistry": [
            "Atomic Structure", "Chemical Bonding", "Chemical Reactions", "Acids and Bases",
            "Organic Chemistry", "Physical Chemistry", "Inorganic Chemistry", "Electrochemistry"
        ],
        "Government": [
            "Nigerian Constitution", "Nigerian Political System", "Nigerian Federalism", 
            "Political Parties", "Electoral Systems", "Public Administration", 
            "Nigerian Foreign Policy", "International Relations"
        ],
        "Literature in English": [
            "Drama", "Poetry", "Prose", "Literary Terms", "African Literature",
            "Non-African Literature", "Literary Criticism", "Literary History"
        ],
        "Economics": [
            "Microeconomics", "Macroeconomics", "Development Economics", "Public Finance",
            "International Economics", "Monetary Economics", "Nigerian Economy", "Economic Theory"
        ],
        "Geography": [
            "Physical Geography", "Human Geography", "Regional Geography", "Map Reading",
            "Environmental Geography", "Economic Geography", "Population Geography", "Climatology"
        ],
        "Agricultural Science": [
            "Soil Science", "Crop Production", "Animal Production", "Agricultural Economics",
            "Farm Mechanization", "Agricultural Ecology", "Fisheries", "Forestry"
        ],
        "Accounting": [
            "Financial Accounting", "Cost Accounting", "Principles of Accounting", "Bookkeeping",
            "Financial Statements", "Partnership Accounting", "Company Accounting", "Public Sector Accounting"
        ],
        "Commerce": [
            "Trade", "Business Organizations", "Marketing", "Money and Banking",
            "Insurance", "Stock Exchange", "Communication", "Consumer Protection"
        ],
        "Christian Religious Studies": [
            "The Bible", "Old Testament", "New Testament", "Church History", 
            "Christian Ethics", "Christian Doctrines", "Christian Living", "Christian Practices"
        ],
        "Islamic Studies": [
            "Qur'an", "Hadith", "Tawhid", "Fiqh", "Islamic History", 
            "Islamic Ethics", "Islamic Civilization", "Islamic Practices"
        ],
        "Computer Science": [
            "Computer Fundamentals", "Programming", "Data Processing", "Database",
            "Computer Networks", "Information Systems", "Software Development", "Computer Applications"
        ]
    }

# ─── IMPROVED QUESTION GENERATION ───────────────────────────────────────────────
def generate_jamb_question(client, subject, difficulty, previous_questions=None):
    """Generate a JAMB-style question with topic diversity"""
    try:
        jamb_topics = get_jamb_subjects_and_topics()
        subject_topics = jamb_topics.get(subject, ["General"])
        topic = random.choice(subject_topics)
        
        if previous_questions:
            used_topics = [q.get("topic", "") for q in previous_questions]
            available_topics = [t for t in subject_topics if t not in used_topics]
            if available_topics:
                topic = random.choice(available_topics)

        prompt = f"""
        Create a {difficulty.lower()} level multiple choice question for {subject} focused on the topic of {topic}.
        This question should follow the Nigerian JAMB curriculum standards and difficulty level.
        
        The question should:
        1. Be specific to Nigerian context when appropriate
        2. Match the depth expected in JAMB exams
        3. Test deep understanding rather than simple memorization
        4. Be distinct from common or standard questions
        5. Include challenging distractors that test common misconceptions
        
        Format your response EXACTLY like this example:
        Question: What is 2 + 2?
        A) 3
        B) 4
        C) 5
        D) 6
        Answer: B
        Explanation: 2 + 2 equals 4, which is option B.
        Topic: Basic Arithmetic
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [{"text": prompt}]}]
        )
        content = response.candidates[0].content.parts[0].text.strip()
        question_data = parse_question_response(content)
        
        if question_data:
            question_data["topic"] = topic
            
            if previous_questions:
                for prev_q in previous_questions:
                    if similarity_check(question_data["question"], prev_q["question"]):
                        return generate_jamb_question(client, subject, difficulty, previous_questions)
            
            return question_data
        return None
    except Exception as e:
        st.error(f"Question generation failed: {str(e)}")
        return None

def similarity_check(question1, question2):
    """Simple check for question similarity to avoid repetition"""
    q1 = ''.join(c.lower() for c in question1 if c.isalnum() or c.isspace())
    q2 = ''.join(c.lower() for c in question2 if c.isalnum() or c.isspace())
    
    if len(q1) > 0 and len(q2) > 0:
        if q1 in q2 or q2 in q1 or (len(set(q1.split()) & set(q2.split())) / len(set(q1.split()) | set(q2.split())) > 0.7):
            return True
    
    return False

def parse_question_response(content):
    """Parse the AI response into structured question data"""
    try:
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        question = ""
        options = []
        answer = ""
        explanation = ""
        topic = ""

        for line in lines:
            if line.startswith("Question:"):
                question = line.replace("Question:", "").strip()
            elif line.startswith(("A)", "B)", "C)", "D)")):
                options.append(line)
            elif line.startswith("Answer:"):
                answer = line.replace("Answer:", "").strip()
            elif line.startswith("Explanation:"):
                explanation = line.replace("Explanation:", "").strip()
            elif line.startswith("Topic:"):
                topic = line.replace("Topic:", "").strip()

        if not all([question, len(options) >= 4, answer, explanation]):
            raise ValueError("Incomplete question data")

        return {
            "question": question,
            "options": options,
            "answer": answer,
            "explanation": explanation,
            "topic": topic
        }
    except Exception:
        return None

# ─── GAMIFICATION FUNCTIONS ───────────────────────────────────────────────────────
def calculate_xp(score, time_efficiency, difficulty_level):
    """Calculate experience points based on quiz performance"""
    base_xp = 100
    score_xp = score * 10
    time_bonus = int(time_efficiency * 50)
    
    difficulty_multiplier = 1.0
    if difficulty_level == "Medium":
        difficulty_multiplier = 1.25
    elif difficulty_level == "Hard":
        difficulty_multiplier = 1.5
        
    total_xp = int((base_xp + score_xp + time_bonus) * difficulty_multiplier)
    return total_xp

def calculate_level(total_xp):
    """Calculate user level based on total XP"""
    level = 1 + int(total_xp / 500)
    return level

def get_xp_progress(total_xp):
    """Calculate progress to next level as percentage"""
    current_level = calculate_level(total_xp)
    xp_for_current_level = (current_level - 1) * 500
    xp_for_next_level = current_level * 500
    
    progress = ((total_xp - xp_for_current_level) / 
                (xp_for_next_level - xp_for_current_level)) * 100
    return int(progress)

def update_streak(last_active_date=None):
    """Update the user's daily streak"""
    today = datetime.now().date()
    
    if not last_active_date:
        return 1, today
        
    if isinstance(last_active_date, str):
        last_active_date = datetime.strptime(last_active_date, "%Y-%m-%d").date()
    
    days_diff = (today - last_active_date).days
    
    if days_diff == 0:
        return st.session_state.streak_count, last_active_date
    elif days_diff == 1:
        return st.session_state.streak_count + 1, today
    else:
        return 1, today

def get_subject_mastery(subject_history):
    """Calculate mastery percentage for each topic in a subject"""
    mastery_data = {}
    
    for entry in subject_history:
        topic = entry.get("topic", "General")
        correct = entry.get("correct", False)
        
        if topic not in mastery_data:
            mastery_data[topic] = {"attempts": 0, "correct": 0}
            
        mastery_data[topic]["attempts"] += 1
        if correct:
            mastery_data[topic]["correct"] += 1
    
    for topic in mastery_data:
        attempts = mastery_data[topic]["attempts"]
        correct = mastery_data[topic]["correct"]
        mastery_data[topic]["mastery"] = int((correct / max(1, attempts)) * 100)
    
    return mastery_data

def check_achievements(user_data):
    """Check and update user achievements"""
    achievements = []
    
    total_quizzes = user_data.get("total_quizzes", 0)
    if total_quizzes >= 1:
        achievements.append({
            "id": "first_quiz",
            "icon": "🎯",
            "title": "First Steps",
            "description": "Completed your first quiz",
            "unlocked": True
        })
    
    if total_quizzes >= 5:
        achievements.append({
            "id": "five_quizzes",
            "icon": "🏅",
            "title": "Quiz Enthusiast",
            "description": "Completed 5 quizzes",
            "unlocked": True
        })
    
    if total_quizzes >= 20:
        achievements.append({
            "id": "twenty_quizzes",
            "icon": "🏆",
            "title": "Quiz Master",
            "description": "Completed 20 quizzes",
            "unlocked": True
        })
    
    perfect_scores = user_data.get("perfect_scores", 0)
    if perfect_scores >= 1:
        achievements.append({
            "id": "first_perfect",
            "icon": "💯",
            "title": "Perfect Start",
            "description": "Got your first perfect score",
            "unlocked": True
        })
    
    if perfect_scores >= 5:
        achievements.append({
            "id": "five_perfect",
            "icon": "🌟",
            "title": "Excellence",
            "description": "Achieved 5 perfect scores",
            "unlocked": True
        })
    
    streak = user_data.get("streak_count", 0)
    if streak >= 3:
        achievements.append({
            "id": "three_day_streak",
            "icon": "🔥",
            "title": "On Fire",
            "description": "3-day study streak",
            "unlocked": True
        })
    
    if streak >= 7:
        achievements.append({
            "id": "weekly_streak",
            "icon": "🔥🔥",
            "title": "Weekly Warrior",
            "description": "7-day study streak",
            "unlocked": True
        })
    
    if streak >= 30:
        achievements.append({
            "id": "monthly_streak",
            "icon": "🔥🔥🔥",
            "title": "Dedication",
            "description": "30-day study streak",
            "unlocked": True
        })
    
    all_achievements = [
        {"id": "first_quiz", "icon": "🎯", "title": "First Steps", "description": "Complete your first quiz"},
        {"id": "five_quizzes", "icon": "🏅", "title": "Quiz Enthusiast", "description": "Complete 5 quizzes"},
        {"id": "twenty_quizzes", "icon": "🏆", "title": "Quiz Master", "description": "Complete 20 quizzes"},
        {"id": "first_perfect", "icon": "💯", "title": "Perfect Start", "description": "Get a perfect score"},
        {"id": "five_perfect", "icon": "🌟", "title": "Excellence", "description": "Achieve 5 perfect scores"},
        {"id": "three_day_streak", "icon": "🔥", "title": "On Fire", "description": "Maintain a 3-day study streak"},
        {"id": "weekly_streak", "icon": "🔥🔥", "title": "Weekly Warrior", "description": "Maintain a 7-day study streak"},
        {"id": "monthly_streak", "icon": "🔥🔥🔥", "title": "Dedication", "description": "Maintain a 30-day study streak"}
    ]
    
    unlocked_ids = [a["id"] for a in achievements]
    for achievement in all_achievements:
        if achievement["id"] not in unlocked_ids:
            locked_achievement = achievement.copy()
            locked_achievement["unlocked"] = False
            achievements.append(locked_achievement)
    
    return sorted(achievements, key=lambda x: (not x["unlocked"], x["title"]))

# ─── TIMER FUNCTIONS ───────────────────────────────────────────────────────────
def format_time_remaining(seconds):
    """Format the remaining time in minutes:seconds"""
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_timer_class(seconds_left):
    """Return the appropriate CSS class for the timer based on time remaining"""
    if seconds_left < 30:
        return "timer timer-danger"
    elif seconds_left < 60:
        return "timer timer-warning"
    else:
        return "timer"

# ─── NAVIGATION FUNCTIONS ──────────────────────────────────────────────────
def go_home():
    """Navigate to home screen and reset quiz state"""
    st.session_state.app_stage = "setup"
    st.session_state.current_question = None
    st.session_state.previous_questions = []
    st.session_state.score = 0
    st.session_state.question_count = 0
    st.session_state.show_answer = False
    st.session_state.user_choice = None
    st.session_state.timer_start = None
    st.session_state.total_time_used = 0
    st.session_state.timer_expired = False
    st.rerun()

def show_navigation_bar():
    """Display the enhanced navigation bar with user stats"""
    current_level = calculate_level(st.session_state.total_xp)
    
    nav_html = f"""
    <div class="nav-bar">
        <div class="nav-title">📘 SmartPrep AI Tutor</div>
        <div class="nav-stats">
            <span class="nav-stat-item">Level {current_level}</span>
            <span class="nav-stat-item">{st.session_state.total_xp} XP</span>
            <span class="nav-stat-item">🔥 {st.session_state.streak_count}</span>
            <span class="nav-stat-item">📊 {st.session_state.total_quizzes}</span>
        </div>
    </div>
    """
    st.markdown(nav_html, unsafe_allow_html=True)

# ─── SESSION STATE INITIALIZATION ───────────────────────────────────────────────
def initialize_session_state():
    """Initialize session state with default values"""
    defaults = {
        "app_stage": "setup",
        "subject": "Mathematics",
        "difficulty": "Medium",
        "current_question": None,
        "previous_questions": [],
        "score": 0,
        "question_count": 0,
        "show_answer": False,
        "user_choice": None,
        "timer_start": None,
        "time_per_question": 120,
        "total_time_used": 0,
        "timer_expired": False,
        "user_name": "Student",
        "total_xp": 0,
        "total_quizzes": 0,
        "perfect_scores": 0,
        "last_active_date": datetime.now().date().isoformat(),
        "streak_count": 1,
        "subject_history": {},
        "achievements": []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ─── ENHANCED VISUALIZATION FUNCTIONS ────────────────────────────────────────────
def create_progress_chart():
    """Create an interactive progress chart"""
    if not st.session_state.subject_history:
        return None
    
    data = []
    for subject, history in st.session_state.subject_history.items():
        mastery_data = get_subject_mastery(history)
        if mastery_data:
            total_attempts = sum(d["attempts"] for d in mastery_data.values())
            total_correct = sum(d["correct"] for d in mastery_data.values())
            overall_mastery = int((total_correct / max(1, total_attempts)) * 100)
            data.append({
                "Subject": subject,
                "Mastery": overall_mastery,
                "Questions": total_attempts
            })
    
    if not data:
        return None
    
    fig = go.Figure(data=[
        go.Bar(
            x=[d["Subject"] for d in data],
            y=[d["Mastery"] for d in data],
            text=[f"{d['Mastery']}%" for d in data],
            textposition='auto',
            marker=dict(
                color=[d["Mastery"] for d in data],
                colorscale='Viridis',
                showscale=False
            ),
            hovertemplate='<b>%{x}</b><br>Mastery: %{y}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Subject Mastery Overview",
        xaxis_title="Subject",
        yaxis_title="Mastery %",
        yaxis_range=[0, 100],
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        font=dict(size=12),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_xp_gauge(current_xp):
    """Create an XP progress gauge"""
    current_level = calculate_level(current_xp)
    xp_for_current = (current_level - 1) * 500
    xp_for_next = current_level * 500
    progress = current_xp - xp_for_current
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=progress,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Level {current_level} Progress", 'font': {'size': 20}},
        delta={'reference': 0, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 500], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 250], 'color': '#e3f2fd'},
                {'range': [250, 500], 'color': '#bbdefb'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 490
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

# ─── USER PROFILE FUNCTIONS ────────────────────────────────────────────────
def show_user_stats():
    """Display comprehensive user statistics with visualizations"""
    current_level = calculate_level(st.session_state.total_xp)
    xp_progress = get_xp_progress(st.session_state.total_xp)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'<div class="level-badge">{current_level}</div>', unsafe_allow_html=True)
        st.markdown(f"### Level {current_level}")
        st.markdown(f"**{st.session_state.total_xp} XP** total")
        st.markdown(f'<div class="xp-bar"><div class="xp-progress" style="width: {xp_progress}%"></div></div>', unsafe_allow_html=True)
        st.markdown(f"<small>**{xp_progress}%** to Level {current_level + 1}</small>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 Statistics")
        st.markdown(f"**Total Quizzes:** {st.session_state.total_quizzes}")
        st.markdown(f"**Perfect Scores:** {st.session_state.perfect_scores}")
        if st.session_state.total_quizzes > 0:
            accuracy = (st.session_state.perfect_scores / st.session_state.total_quizzes) * 100
            st.markdown(f"**Perfect Rate:** {accuracy:.1f}%")
    
    with col3:
        st.markdown("### 🔥 Streak")
        if st.session_state.streak_count > 1:
            st.markdown(f'<span class="streak-flame">🔥</span> **{st.session_state.streak_count} days**', unsafe_allow_html=True)
        else:
            st.markdown("**1 day** streak!")
        st.markdown(f"<small>Last active: {st.session_state.last_active_date}</small>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show progress chart
    chart = create_progress_chart()
    if chart:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.plotly_chart(chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_subject_progress():
    """Display detailed progress across subjects"""
    if not st.session_state.subject_history:
        return
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📚 Subject Progress")
    
    for subject, history in st.session_state.subject_history.items():
        mastery_data = get_subject_mastery(history)
        if mastery_data:
            st.markdown(f'<span class="subject-badge">{subject}</span>', unsafe_allow_html=True)
            
            total_attempts = sum(data["attempts"] for data in mastery_data.values())
            total_correct = sum(data["correct"] for data in mastery_data.values())
            overall_mastery = int((total_correct / max(1, total_attempts)) * 100)
            
            st.markdown(f"**Overall: {overall_mastery}%** ({total_correct}/{total_attempts})")
            st.markdown(f'<div class="mastery-bar"><div class="mastery-progress" style="width: {overall_mastery}%"></div></div>', unsafe_allow_html=True)
            
            with st.expander(f"📖 View {subject} topics"):
                for topic, data in sorted(mastery_data.items(), key=lambda x: x[1]["mastery"], reverse=True):
                    mastery_percent = data["mastery"]
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{topic}**")
                        st.markdown(f'<div class="mastery-bar"><div class="mastery-progress" style="width: {mastery_percent}%"></div></div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"**{mastery_percent}%**")
                        st.markdown(f"<small>{data['correct']}/{data['attempts']}</small>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ─── MAIN APPLICATION ───────────────────────────────────────────────────────────
def main():
    initialize_session_state()
    client = initialize_client()
    
    if st.session_state.app_stage != "setup":
        show_navigation_bar()
        
        # Home button
        if st.button("🏠 Home", key="home_btn"):
            go_home()
    
    if st.session_state.app_stage == "setup":
        st.markdown("""
        <div class="main-header">
            <h1>📘 SmartPrep AI Tutor</h1>
            <p>JAMB Edition - Your Path to Excellence</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.app_stage == "setup":
        show_setup_screen(client)
    elif st.session_state.app_stage == "quiz":
        show_quiz_screen(client)
    elif st.session_state.app_stage == "results":
        show_results_screen()

def show_setup_screen(client):
    """Enhanced setup screen"""
    if st.session_state.total_quizzes > 0:
        show_user_stats()
        show_subject_progress()
        
        # Achievements section
        user_data = {
            "total_quizzes": st.session_state.total_quizzes,
            "perfect_scores": st.session_state.perfect_scores,
            "streak_count": st.session_state.streak_count,
            "subject_history": st.session_state.subject_history
        }
        
        achievements = check_achievements(user_data)
        unlocked = [a for a in achievements if a["unlocked"]]
        
        if unlocked:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 🏆 Recent Achievements")
            cols = st.columns(min(3, len(unlocked)))
            for i, ach in enumerate(unlocked[:3]):
                with cols[i]:
                    st.markdown(f"""
                    <div class="achievement-card">
                        <div class="achievement-icon">{ach["icon"]}</div>
                        <div class="achievement-content">
                            <strong>{ach["title"]}</strong><br>
                            <small>{ach["description"]}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
    st.markdown("## 🚀 Start New Quiz")
    
    subjects_info = {
        "Mathematics": "🔢 Algebra, Geometry, Statistics",
        "Biology": "🧬 Life sciences & genetics",
        "English Language": "📝 Grammar & comprehension",
        "Physics": "⚛️ Mechanics & modern physics",
        "Chemistry": "🧪 Chemical reactions & bonding",
        "Government": "🏛️ Nigerian politics & governance",
        "Literature in English": "📚 Drama, poetry & prose",
        "Economics": "💰 Micro & macroeconomics",
        "Geography": "🌍 Physical & human geography",
        "Agricultural Science": "🌾 Crop & animal production",
        "Accounting": "📊 Financial accounting",
        "Commerce": "🏢 Trade & business",
        "Christian Religious Studies": "✝️ Bible & Christian teachings",
        "Islamic Studies": "☪️ Qur'an & Islamic principles",
        "Computer Science": "💻 Programming & IT systems"
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.selectbox(
            "📚 Choose Subject:",
            list(subjects_info.keys()),
            index=0
        )
        st.markdown(f'<div class="info-box">{subjects_info[subject]}</div>', unsafe_allow_html=True)
    
    with col2:
        difficulty = st.selectbox(
            "🎯 Difficulty Level:",
            ["Easy", "Medium", "Hard"],
            index=1
        )
        diff_info = {
            "Easy": "✅ Perfect for beginners",
            "Medium": "⚖️ Standard JAMB level", 
            "Hard": "🎯 Advanced preparation"
        }
        st.markdown(f'<div class="info-box">{diff_info[difficulty]}</div>', unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Quiz Settings")
    time_options = {
        "60 seconds": 60,
        "90 seconds": 90, 
        "2 minutes (Recommended)": 120,
        "3 minutes": 180,
        "No time limit": None
    }
    
    time_choice = st.selectbox("⏱️ Time per question:", list(time_options.keys()), index=2)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
        with st.spinner("🔄 Generating your first question..."):
            st.session_state.subject = subject
            st.session_state.difficulty = difficulty
            st.session_state.time_per_question = time_options[time_choice]
            
            question = generate_jamb_question(client, subject, difficulty)
            
            if question:
                st.session_state.current_question = question
                st.session_state.previous_questions = [question]
                st.session_state.app_stage = "quiz"
                st.session_state.question_count = 1
                st.session_state.timer_start = time.time() if time_options[time_choice] else None
                st.success("✅ Question generated!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ Failed to generate question. Please try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_quiz_screen(client):
    """Enhanced quiz screen"""
    if not st.session_state.current_question:
        st.error("No question available. Returning to setup...")
        st.session_state.app_stage = "setup"
        st.rerun()
        return
    
    question = st.session_state.current_question
    
    # Timer display
    if st.session_state.timer_start and st.session_state.time_per_question and not st.session_state.show_answer:
        elapsed = time.time() - st.session_state.timer_start
        time_left = max(0, st.session_state.time_per_question - elapsed)
        
        timer_class = get_timer_class(time_left)
        st.markdown(f'<div class="{timer_class}">⏱️ {format_time_remaining(int(time_left))}</div>', unsafe_allow_html=True)
        
        if time_left <= 0 and not st.session_state.timer_expired:
            st.session_state.timer_expired = True
            st.session_state.show_answer = True
            st.session_state.user_choice = "Time Expired"
            st.rerun()
    
    # Progress
    progress = st.session_state.question_count / 10
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    st.markdown(f"**Question {st.session_state.question_count} of 10** ({int(progress * 100)}%)")
    st.progress(progress)
    current_score = st.session_state.score
    attempted = st.session_state.question_count - (1 if not st.session_state.show_answer else 0)
    if attempted > 0:
        st.markdown(f"**Score: {current_score}/{attempted}** ({int((current_score/attempted)*100)}%)")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
    
    st.markdown(f'<span class="subject-badge">{st.session_state.subject}</span>', unsafe_allow_html=True)
    st.markdown(f"**Topic:** {question.get('topic', 'General')} | **Difficulty:** {st.session_state.difficulty}")
    st.markdown("---")
    st.markdown(f"### {question['question']}")
    
    if not st.session_state.show_answer:
        choice = st.radio(
            "Select your answer:",
            question['options'],
            key=f"q_{st.session_state.question_count}"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ Submit Answer", type="primary", use_container_width=True):
                st.session_state.user_choice = choice
                st.session_state.show_answer = True
                
                if st.session_state.timer_start:
                    time_used = time.time() - st.session_state.timer_start
                    st.session_state.total_time_used += time_used
                
                is_correct = choice.startswith(question['answer'])
                if is_correct:
                    st.session_state.score += 1
                
                if st.session_state.subject not in st.session_state.subject_history:
                    st.session_state.subject_history[st.session_state.subject] = []
                
                st.session_state.subject_history[st.session_state.subject].append({
                    "topic": question.get("topic", "General"),
                    "correct": is_correct,
                    "date": datetime.now().isoformat(),
                    "difficulty": st.session_state.difficulty
                })
                
                st.rerun()
    
    if st.session_state.show_answer:
        user_answer = st.session_state.user_choice
        correct_answer = question['answer']
        
        if user_answer == "Time Expired":
            st.markdown(f'<div class="error-msg">⏰ <strong>Time Expired!</strong> Correct answer: <strong>{correct_answer}</strong></div>', unsafe_allow_html=True)
        elif user_answer.startswith(correct_answer):
            st.markdown('<div class="success-msg">✅ <strong>Correct!</strong> Excellent work! 🎉</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-msg">❌ <strong>Incorrect.</strong> Correct answer: <strong>{correct_answer}</strong></div>', unsafe_allow_html=True)
        
        st.markdown("### 💡 Explanation")
        st.markdown(f'<div class="info-box">{question["explanation"]}</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.session_state.question_count >= 10:
                if st.button("🎯 View Results", type="primary", use_container_width=True):
                    st.session_state.app_stage = "results"
                    st.rerun()
            else:
                if st.button("➡️ Next Question", type="primary", use_container_width=True):
                    with st.spinner("🔄 Loading..."):
                        next_q = generate_jamb_question(
                            client, 
                            st.session_state.subject, 
                            st.session_state.difficulty,
                            st.session_state.previous_questions
                        )
                        
                        if next_q:
                            st.session_state.current_question = next_q
                            st.session_state.previous_questions.append(next_q)
                            st.session_state.question_count += 1
                            st.session_state.show_answer = False
                            st.session_state.user_choice = None
                            st.session_state.timer_start = time.time() if st.session_state.time_per_question else None
                            st.session_state.timer_expired = False
                            st.rerun()
                        else:
                            st.error("Failed to generate question.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_results_screen():
    """Enhanced results screen"""
    st.balloons()
    
    score_percentage = (st.session_state.score / 10) * 100
    time_efficiency = max(0, (1200 - st.session_state.total_time_used) / 1200) if st.session_state.total_time_used > 0 else 1
    
    xp_earned = calculate_xp(st.session_state.score, time_efficiency, st.session_state.difficulty)
    old_xp = st.session_state.total_xp
    old_level = calculate_level(old_xp)
    
    st.session_state.total_xp += xp_earned
    st.session_state.total_quizzes += 1
    
    if st.session_state.score == 10:
        st.session_state.perfect_scores += 1
    
    new_level = calculate_level(st.session_state.total_xp)
    level_up = new_level > old_level
    
    st.session_state.streak_count, st.session_state.last_active_date = update_streak(
        st.session_state.last_active_date
    )
    
    st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
    
    if level_up:
        st.markdown(f'<div class="success-msg">🎉 <strong>LEVEL UP!</strong> You reached Level {new_level}! 🚀</div>', unsafe_allow_html=True)
    
    st.markdown("## 🎉 Quiz Complete!")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### 📊 Score")
        st.markdown(f"**{st.session_state.score}/10**")
        st.markdown(f"**{score_percentage:.0f}%**")
    
    with col2:
        st.markdown("### ⏱️ Time")
        if st.session_state.total_time_used > 0:
            mins = st.session_state.total_time_used / 60
            st.markdown(f"**{mins:.1f} min**")
        else:
            st.markdown("**Untimed**")
    
    with col3:
        st.markdown("### ⭐ XP")
        st.markdown(f"**+{xp_earned}**")
        st.markdown(f"Total: {st.session_state.total_xp}")
    
    with col4:
        st.markdown("### 🎯 Level")
        st.markdown(f'<div class="level-badge">{new_level}</div>', unsafe_allow_html=True)
    
    # Feedback
    if score_percentage == 100:
        st.markdown('<div class="success-msg">🌟 <strong>PERFECT SCORE!</strong> Outstanding! 🏆</div>', unsafe_allow_html=True)
    elif score_percentage >= 80:
        st.markdown('<div class="success-msg">🌟 <strong>Excellent!</strong> Keep it up! 👏</div>', unsafe_allow_html=True)
    elif score_percentage >= 60:
        st.markdown('<div class="info-box">👍 <strong>Good job!</strong> You\'re on track! 💪</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="warning-box">📚 <strong>Keep practicing!</strong> You\'ve got this! 🎯</div>', unsafe_allow_html=True)
    
    # XP Progress
    xp_progress = get_xp_progress(st.session_state.total_xp)
    st.markdown("### 🚀 Progress")
    st.markdown(f'<div class="level-badge">{new_level}</div> **Level {new_level}** - {st.session_state.total_xp} XP', unsafe_allow_html=True)
    st.markdown(f'<div class="xp-bar"><div class="xp-progress" style="width: {xp_progress}%"></div></div>', unsafe_allow_html=True)
    st.markdown(f"**{xp_progress}%** to Level {new_level + 1}")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Quiz", type="primary", use_container_width=True):
            go_home()
    
    with col2:
        if st.button("📊 Dashboard", use_container_width=True):
            go_home()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
