import streamlit as st
from google import genai
import time
import random
from datetime import datetime, timedelta
import json
import hashlib
import base64
from io import BytesIO

# ─── PAGE CONFIGURATION ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="📘 SmartPrep AI Tutor - JAMB Edition",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── ENHANCED STYLING WITH GAMIFICATION AND NAVIGATION ──────────────────────────
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
    .timer {
        background: #e2f0fb;
        color: #0c63e4;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        text-align: center;
        font-size: 1.25rem;
        font-weight: bold;
    }
    .timer-warning {
        background: #fff3cd;
        color: #856404;
    }
    .timer-danger {
        background: #f8d7da;
        color: #721c24;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .subject-badge {
        display: inline-block;
        background: #4f46e5;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .achievement-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #dee2e6;
        display: flex;
        align-items: center;
        transition: transform 0.2s;
    }
    .achievement-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .achievement-locked {
        filter: grayscale(1);
        opacity: 0.7;
    }
    .achievement-icon {
        font-size: 2rem;
        margin-right: 1rem;
        min-width: 2.5rem;
        text-align: center;
    }
    .achievement-content {
        flex-grow: 1;
    }
    .streak-flame {
        color: #ff9800;
        font-size: 1.5rem;
        animation: flicker 1.5s infinite alternate;
    }
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { opacity: 1; }
        20%, 24%, 55% { opacity: 0.5; }
    }
    .leaderboard-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        background: white;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .leaderboard-rank {
        font-weight: bold;
        width: 3rem;
        text-align: center;
        font-size: 1.25rem;
    }
    .leaderboard-user {
        flex-grow: 1;
        margin-left: 1rem;
    }
    .leaderboard-score {
        font-weight: bold;
        text-align: right;
        color: #4f46e5;
    }
    .xp-bar {
        height: 0.75rem;
        background: #e9ecef;
        border-radius: 0.5rem;
        margin-top: 0.5rem;
        overflow: hidden;
    }
    .xp-progress {
        height: 100%;
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        border-radius: 0.5rem;
        transition: width 0.5s ease;
    }
    .level-badge {
        display: inline-block;
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        font-weight: bold;
        width: 2.5rem;
        height: 2.5rem;
        line-height: 2.5rem;
        text-align: center;
        border-radius: 50%;
        margin-right: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .tab-container {
        display: flex;
        border-bottom: 2px solid #e9ecef;
        margin-bottom: 1.5rem;
        background: white;
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 0.25rem;
    }
    .tab-button {
        flex: 1;
        padding: 0.75rem 1rem;
        margin: 0.25rem;
        cursor: pointer;
        border: none;
        background: transparent;
        font-weight: 600;
        border-radius: 0.25rem;
        transition: all 0.3s;
    }
    .tab-button:hover {
        background: #f8f9fa;
    }
    .tab-button.active {
        background: #4f46e5;
        color: white;
    }
    .mastery-bar {
        height: 0.5rem;
        background: #e9ecef;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    .mastery-progress {
        height: 100%;
        background: linear-gradient(90deg, #12b886 0%, #38d9a9 100%);
        border-radius: 0.25rem;
    }
    .points-highlight {
        font-weight: bold;
        color: #4f46e5;
        font-size: 1.5rem;
    }
    .home-button {
        position: fixed;
        top: 1rem;
        left: 1rem;
        background: #6c757d;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        z-index: 1000;
        transition: background 0.3s;
    }
    .home-button:hover {
        background: #5a6268;
    }
    .feature-card {
        background: white;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .daily-challenge {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    .motivational-quote {
        background: #f8f9fa;
        border-left: 4px solid #4f46e5;
        padding: 1rem;
        margin: 1rem 0;
        font-style: italic;
    }
    .subject-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 0.75rem;
        margin: 1rem 0;
    }
    .subject-card {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    .subject-card:hover {
        border-color: #4f46e5;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .subject-card.selected {
        background: #4f46e5;
        color: white;
        border-color: #4f46e5;
    }
    .progress-ring {
        width: 120px;
        height: 120px;
        margin: 0 auto;
    }
    .progress-ring-circle {
        stroke: #4f46e5;
        stroke-width: 8;
        fill: transparent;
        stroke-dasharray: 314;
        stroke-dashoffset: 314;
        transform: rotate(-90deg);
        transform-origin: 50% 50%;
        transition: stroke-dashoffset 0.5s;
    }
    .study-tip {
        background: #e7f3ff;
        border: 1px solid #2196F3;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .study-tip-icon {
        color: #2196F3;
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── MOTIVATIONAL QUOTES ─────────────────────────────────────────────────────────
MOTIVATIONAL_QUOTES = [
    "Success is not final, failure is not fatal: it is the courage to continue that counts.",
    "The expert in anything was once a beginner.",
    "Education is the passport to the future, for tomorrow belongs to those who prepare for it today.",
    "Your JAMB success story starts with every question you practice today.",
    "Small daily improvements over time create stunning results.",
    "The only way to do great work is to love what you do.",
    "Believe you can and you're halfway there.",
    "Success doesn't come from what you do occasionally, but what you do consistently.",
    "Every accomplishment starts with the decision to try.",
    "The beautiful thing about learning is that no one can take it away from you."
]

# ─── USER MANAGEMENT SYSTEM ──────────────────────────────────────────────────────
class UserManager:
    @staticmethod
    def initialize_user_data():
        """Initialize user data structure"""
        if 'user_data' not in st.session_state:
            st.session_state.user_data = {
                'username': '',
                'total_xp': 0,
                'level': 1,
                'streak': 0,
                'last_activity': datetime.now().isoformat(),
                'subjects_progress': {},
                'achievements': [],
                'quiz_history': [],
                'daily_challenges_completed': [],
                'total_questions_answered': 0,
                'correct_answers': 0
            }
    
    @staticmethod
    def create_user_profile():
        """Create or load user profile"""
        st.subheader("👤 User Profile Setup")
        
        username = st.text_input("Enter your username:", value=st.session_state.user_data.get('username', ''))
        
        if st.button("Save Profile") and username:
            st.session_state.user_data['username'] = username
            st.success(f"Welcome, {username}! Your profile has been saved.")
            st.rerun()
    
    @staticmethod
    def calculate_level(xp):
        """Calculate user level based on XP"""
        return min(100, max(1, int(xp / 100) + 1))
    
    @staticmethod
    def update_streak():
        """Update user streak based on daily activity"""
        last_activity = datetime.fromisoformat(st.session_state.user_data['last_activity'])
        today = datetime.now().date()
        last_activity_date = last_activity.date()
        
        if last_activity_date == today:
            return  # Already active today
        elif last_activity_date == today - timedelta(days=1):
            st.session_state.user_data['streak'] += 1
        else:
            st.session_state.user_data['streak'] = 1
        
        st.session_state.user_data['last_activity'] = datetime.now().isoformat()

# ─── ACHIEVEMENT SYSTEM ───────────────────────────────────────────────────────────
class AchievementSystem:
    ACHIEVEMENTS = {
        'first_quiz': {'icon': '🎯', 'title': 'First Steps', 'description': 'Complete your first quiz', 'xp': 50},
        'streak_7': {'icon': '🔥', 'title': 'Week Warrior', 'description': '7-day streak', 'xp': 100},
        'streak_30': {'icon': '🏆', 'title': 'Monthly Master', 'description': '30-day streak', 'xp': 500},
        'perfect_score': {'icon': '💯', 'title': 'Perfectionist', 'description': 'Get 100% on a quiz', 'xp': 200},
        'speed_demon': {'icon': '⚡', 'title': 'Speed Demon', 'description': 'Complete quiz in under 5 minutes', 'xp': 150},
        'knowledge_seeker': {'icon': '📚', 'title': 'Knowledge Seeker', 'description': 'Answer 100 questions', 'xp': 300},
        'subject_master': {'icon': '🎓', 'title': 'Subject Master', 'description': 'Master a subject (80%+ average)', 'xp': 400}
    }
    
    @staticmethod
    def check_achievements(quiz_result=None):
        """Check and award new achievements"""
        user_data = st.session_state.user_data
        new_achievements = []
        
        # First quiz achievement
        if 'first_quiz' not in user_data['achievements'] and len(user_data['quiz_history']) >= 1:
            new_achievements.append('first_quiz')
        
        # Streak achievements
        if user_data['streak'] >= 7 and 'streak_7' not in user_data['achievements']:
            new_achievements.append('streak_7')
        if user_data['streak'] >= 30 and 'streak_30' not in user_data['achievements']:
            new_achievements.append('streak_30')
        
        # Perfect score achievement
        if quiz_result and quiz_result['score'] == 100 and 'perfect_score' not in user_data['achievements']:
            new_achievements.append('perfect_score')
        
        # Questions answered achievement
        if user_data['total_questions_answered'] >= 100 and 'knowledge_seeker' not in user_data['achievements']:
            new_achievements.append('knowledge_seeker')
        
        # Award new achievements
        for achievement in new_achievements:
            user_data['achievements'].append(achievement)
            user_data['total_xp'] += AchievementSystem.ACHIEVEMENTS[achievement]['xp']
            st.success(f"🎉 Achievement Unlocked: {AchievementSystem.ACHIEVEMENTS[achievement]['title']}!")
    
    @staticmethod
    def display_achievements():
        """Display user achievements"""
        st.subheader("🏆 Achievements")
        
        col1, col2 = st.columns(2)
        for i, (key, achievement) in enumerate(AchievementSystem.ACHIEVEMENTS.items()):
            col = col1 if i % 2 == 0 else col2
            
            is_unlocked = key in st.session_state.user_data['achievements']
            card_class = "achievement-card" if is_unlocked else "achievement-card achievement-locked"
            
            with col:
                st.markdown(f"""
                <div class="mastery-bar">
                    <div class="mastery-progress" style="width: {mastery_percent}%"></div>
                </div>
                """, unsafe_allow_html=True)
                st.write(f"Average Score: {progress['average_score']:.1f}% | Quizzes Taken: {progress['total_quizzes']}")
        
        # Recent quiz history
        if user_data['quiz_history']:
            st.subheader("📋 Recent Quiz History")
            recent_quizzes = sorted(user_data['quiz_history'], key=lambda x: x['timestamp'], reverse=True)[:5]
            
            for quiz in recent_quizzes:
                with st.expander(f"{quiz['subject']} - {quiz['topic']} ({quiz['score']:.1f}%)"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Score:** {quiz['correct']}/{quiz['total']} ({quiz['score']:.1f}%)")
                    with col2:
                        st.write(f"**Time:** {quiz['duration']//60}:{quiz['duration']%60:02d}")
                    with col3:
                        st.write(f"**XP Earned:** {quiz['xp_earned']}")
    
    @staticmethod
    def display_subject_analytics(subject):
        """Display detailed analytics for a specific subject"""
        user_data = st.session_state.user_data
        subject_quizzes = [q for q in user_data['quiz_history'] if q['subject'] == subject]
        
        if not subject_quizzes:
            st.info(f"No quiz data available for {subject} yet. Take a quiz to see your progress!")
            return
        
        st.subheader(f"📊 {subject} Analytics")
        
        # Performance over time
        scores = [q['score'] for q in subject_quizzes]
        avg_score = sum(scores) / len(scores)
        best_score = max(scores)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Score", f"{avg_score:.1f}%")
        with col2:
            st.metric("Best Score", f"{best_score:.1f}%")
        with col3:
            st.metric("Quizzes Taken", len(subject_quizzes))
        
        # Topic breakdown
        topic_performance = {}
        for quiz in subject_quizzes:
            topic = quiz['topic']
            if topic not in topic_performance:
                topic_performance[topic] = []
            topic_performance[topic].append(quiz['score'])
        
        if topic_performance:
            st.subheader("📈 Topic Performance")
            for topic, scores in topic_performance.items():
                avg_score = sum(scores) / len(scores)
                st.write(f"**{topic}:** {avg_score:.1f}% average ({len(scores)} quiz{'s' if len(scores) > 1 else ''})")
                st.progress(avg_score / 100)

# ─── DAILY CHALLENGES SYSTEM ──────────────────────────────────────────────────────
class DailyChallenges:
    @staticmethod
    def get_daily_challenge():
        """Generate or retrieve today's daily challenge"""
        today = datetime.now().date().isoformat()
        
        # Check if already completed today
        if today in st.session_state.user_data['daily_challenges_completed']:
            return None
        
        # Generate challenge based on date (consistent daily challenge)
        random.seed(today)
        subjects = list(get_jamb_subjects_and_topics().keys())
        challenge_subject = random.choice(subjects)
        topics = get_jamb_subjects_and_topics()[challenge_subject]
        challenge_topic = random.choice(topics)
        
        return {
            'subject': challenge_subject,
            'topic': challenge_topic,
            'xp_reward': 100,
            'description': f"Complete a quiz on {challenge_topic} in {challenge_subject}"
        }
    
    @staticmethod
    def display_daily_challenge():
        """Display today's daily challenge"""
        challenge = DailyChallenges.get_daily_challenge()
        
        if not challenge:
            st.markdown("""
            <div class="daily-challenge">
                <h3>🎉 Daily Challenge Complete!</h3>
                <p>You've completed today's challenge. Come back tomorrow for a new one!</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        st.markdown(f"""
        <div class="daily-challenge">
            <h3>🏆 Daily Challenge</h3>
            <p><strong>{challenge['description']}</strong></p>
            <p>Reward: <span class="points-highlight">+{challenge['xp_reward']} XP</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Accept Challenge"):
            st.session_state.selected_subject = challenge['subject']
            st.session_state.selected_topic = challenge['topic']
            st.session_state.is_daily_challenge = True
            st.session_state.current_page = 'quiz'
            st.rerun()
    
    @staticmethod
    def complete_daily_challenge():
        """Mark daily challenge as complete and award XP"""
        today = datetime.now().date().isoformat()
        if today not in st.session_state.user_data['daily_challenges_completed']:
            st.session_state.user_data['daily_challenges_completed'].append(today)
            st.session_state.user_data['total_xp'] += 100
            st.success("🎉 Daily Challenge Complete! +100 XP Bonus!")

# ─── STUDY TIPS SYSTEM ────────────────────────────────────────────────────────────
class StudyTipsSystem:
    STUDY_TIPS = {
        'Mathematics': [
            "Practice solving problems step by step and show all your work.",
            "Use visual aids like graphs and diagrams to understand complex concepts.",
            "Master basic arithmetic and algebra before moving to advanced topics.",
            "Time yourself when solving problems to improve speed."
        ],
        'Biology': [
            "Create concept maps to connect related biological processes.",
            "Use mnemonics to remember complex biological terms and processes.",
            "Practice drawing and labeling biological diagrams.",
            "Relate biological concepts to everyday life examples."
        ],
        'English Language': [
            "Read extensively to improve vocabulary and comprehension skills.",
            "Practice identifying grammatical structures in sentences.",
            "Learn common prefixes, suffixes, and root words.",
            "Practice writing essays with clear structure and proper grammar."
        ],
        'Physics': [
            "Understand the fundamental concepts before memorizing formulas.",
            "Practice numerical problems regularly to build problem-solving skills.",
            "Visualize physical phenomena using diagrams and illustrations.",
            "Connect physics concepts to real-world applications."
        ],
        'Chemistry': [
            "Master the periodic table and understand element properties.",
            "Practice balancing chemical equations regularly.",
            "Understand the 'why' behind chemical reactions, not just the 'what'.",
            "Use molecular models to visualize chemical structures."
        ],
        'Government': [
            "Stay updated with current political events and developments.",
            "Understand the structure and functions of government institutions.",
            "Practice analyzing political scenarios and their implications.",
            "Compare Nigerian political system with other democratic systems."
        ]
    }
    
    @staticmethod
    def get_random_tip(subject=None):
        """Get a random study tip, optionally for a specific subject"""
        if subject and subject in StudyTipsSystem.STUDY_TIPS:
            return random.choice(StudyTipsSystem.STUDY_TIPS[subject])
        else:
            all_tips = []
            for tips in StudyTipsSystem.STUDY_TIPS.values():
                all_tips.extend(tips)
            return random.choice(all_tips)
    
    @staticmethod
    def display_study_tips(subject):
        """Display study tips for a specific subject"""
        if subject in StudyTipsSystem.STUDY_TIPS:
            st.subheader(f"💡 Study Tips for {subject}")
            tips = StudyTipsSystem.STUDY_TIPS[subject]
            for i, tip in enumerate(tips, 1):
                st.markdown(f"""
                <div class="study-tip">
                    <span class="study-tip-icon">💡</span>
                    <strong>Tip {i}:</strong> {tip}
                </div>
                """, unsafe_allow_html=True)

# ─── API CLIENT SETUP ────────────────────────────────────────────────────────────
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
            "Calculus", "Vectors", "Matrices", "Number Bases", "Sets and Logic",
            "Indices and Logarithms", "Surds", "Sequence and Series", "Permutation and Combination"
        ],
        "Biology": [
            "Cell Biology", "Genetics", "Ecology", "Evolution", "Plant Biology", "Animal Biology",
            "Human Anatomy and Physiology", "Microbiology", "Reproduction", "Nutrition",
            "Respiration", "Excretion", "Growth and Development", "Coordination and Control"
        ],
        "English Language": [
            "Comprehension", "Lexis and Structure", "Oral Forms", "Figurative Expressions",
            "Literary Devices", "Registers", "Synonyms and Antonyms", "Grammatical Structures",
            "Essay Writing", "Summary", "Vowels and Consonants", "Stress and Intonation"
        ],
        "Physics": [
            "Mechanics", "Energy", "Waves", "Optics", "Electricity and Magnetism", 
            "Modern Physics", "Heat and Temperature", "Electronics", "Nuclear Physics",
            "Motion", "Forces", "Work and Power", "Simple Machines"
        ],
        "Chemistry": [
            "Atomic Structure", "Chemical Bonding", "Chemical Reactions", "Acids and Bases",
            "Organic Chemistry", "Physical Chemistry", "Inorganic Chemistry", "Electrochemistry",
            "Rates of Reaction", "Chemical Equilibrium", "Redox Reactions", "Thermodynamics"
        ],
        "Government": [
            "Nigerian Constitution", "Nigerian Political System", "Nigerian Federalism", 
            "Political Parties", "Electoral Systems", "Public Administration", 
            "Nigerian Foreign Policy", "International Relations", "Democracy", "Rule of Law",
            "Separation of Powers", "Pressure Groups"
        ]
    }

# ─── MAIN APPLICATION PAGES ───────────────────────────────────────────────────────
def show_home_page():
    """Display the main home page with navigation options"""
    # Display main header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("📘 SmartPrep AI Tutor - JAMB Edition")
    st.markdown("Your intelligent companion for JAMB preparation")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display motivational quote
    quote = random.choice(MOTIVATIONAL_QUOTES)
    st.markdown(f'<div class="motivational-quote">💡 {quote}</div>', unsafe_allow_html=True)
    
    # User profile section
    if not st.session_state.user_data['username']:
        UserManager.create_user_profile()
        return
    
    # Welcome message with user stats
    user_data = st.session_state.user_data
    st.markdown(f"""
    <div class="stats-card">
        <h2>Welcome back, {user_data['username']}! 👋</h2>
        <p>Level {user_data['level']} • {user_data['total_xp']} XP • {user_data['streak']} day streak</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Daily Challenge
    DailyChallenges.display_daily_challenge()
    
    # Feature cards
    st.subheader("🚀 What would you like to do?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <h3>Take a Quiz</h3>
            <p>Practice with AI-generated questions tailored to JAMB syllabus</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Quiz", key="start_quiz"):
            st.session_state.current_page = 'subject_selection'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <h3>View Progress</h3>
            <p>Track your performance and see detailed analytics</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Progress", key="view_progress"):
            st.session_state.current_page = 'progress'
            st.rerun()
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🏆</div>
            <h3>Achievements</h3>
            <p>Check your unlocked achievements and earn rewards</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Achievements", key="view_achievements"):
            st.session_state.current_page = 'achievements'
            st.rerun()
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💡</div>
            <h3>Study Tips</h3>
            <p>Get personalized study recommendations and tips</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Study Tips", key="study_tips"):
            st.session_state.current_page = 'study_tips'
            st.rerun()

def show_subject_selection():
    """Display subject and topic selection interface"""
    st.markdown('<a href="#" class="home-button" onclick="window.location.reload()">🏠 Home</a>', unsafe_allow_html=True)
    
    st.title("📚 Choose Your Subject")
    st.write("Select a subject and topic for your quiz")
    
    subjects_topics = get_jamb_subjects_and_topics()
    
    # Subject selection
    st.subheader("Select Subject")
    selected_subject = st.selectbox("Choose a subject:", list(subjects_topics.keys()))
    
    if selected_subject:
        # Display subject grid for visual selection
        st.markdown('<div class="subject-grid">', unsafe_allow_html=True)
        for subject in subjects_topics.keys():
            selected_class = "selected" if subject == selected_subject else ""
            st.markdown(f"""
            <div class="subject-card {selected_class}">
                <h4>{subject}</h4>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Topic selection
        st.subheader(f"Select Topic from {selected_subject}")
        topics = subjects_topics[selected_subject]
        selected_topic = st.selectbox("Choose a topic:", topics)
        
        # Difficulty selection
        st.subheader("Select Difficulty")
        difficulty = st.selectbox("Choose difficulty level:", ["easy", "medium", "hard"])
        
        # Number of questions
        num_questions = st.slider("Number of questions:", min_value=3, max_value=10, value=5)
        
        # Display study tips for selected subject
        StudyTipsSystem.display_study_tips(selected_subject)
        
        # Start quiz button
        if st.button("🚀 Generate Quiz", type="primary"):
            st.session_state.selected_subject = selected_subject
            st.session_state.selected_topic = selected_topic
            st.session_state.selected_difficulty = difficulty
            st.session_state.num_questions = num_questions
            st.session_state.current_page = 'quiz'
            st.rerun()

def show_quiz_page(client):
    """Display the quiz interface"""
    st.markdown('<a href="#" class="home-button" onclick="window.location.reload()">🏠 Home</a>', unsafe_allow_html=True)
    
    subject = st.session_state.get('selected_subject', 'Mathematics')
    topic = st.session_state.get('selected_topic', 'Algebra')
    difficulty = st.session_state.get('selected_difficulty', 'medium')
    num_questions = st.session_state.get('num_questions', 5)
    
    # Generate questions if not already done
    if 'current_quiz_questions' not in st.session_state:
        with st.spinner("🤖 Generating quiz questions..."):
            questions = QuizGenerator.generate_questions(client, subject, topic, difficulty, num_questions)
            st.session_state.current_quiz_questions = questions
    
    questions = st.session_state.current_quiz_questions
    
    if questions:
        QuizGenerator.display_quiz(questions, subject, topic)
        
        # Check if this was a daily challenge
        if st.session_state.get('is_daily_challenge', False) and st.session_state.quiz_state.get('submitted', False):
            DailyChallenges.complete_daily_challenge()
            st.session_state.is_daily_challenge = False
    else:
        st.error("Failed to generate quiz questions. Please try again.")
        if st.button("Back to Subject Selection"):
            st.session_state.current_page = 'subject_selection'
            st.rerun()

def show_progress_page():
    """Display the progress tracking page"""
    st.markdown('<a href="#" class="home-button" onclick="window.location.reload()">🏠 Home</a>', unsafe_allow_html=True)
    
    ProgressTracker.display_dashboard()
    
    # Subject-specific analytics
    user_data = st.session_state.user_data
    if user_data['subjects_progress']:
        st.subheader("📊 Subject Analytics")
        selected_subject = st.selectbox("Select subject for detailed analytics:", 
                                       list(user_data['subjects_progress'].keys()))
        if selected_subject:
            ProgressTracker.display_subject_analytics(selected_subject)

def show_achievements_page():
    """Display the achievements page"""
    st.markdown('<a href="#" class="home-button" onclick="window.location.reload()">🏠 Home</a>', unsafe_allow_html=True)
    
    AchievementSystem.display_achievements()

def show_study_tips_page():
    """Display the study tips page"""
    st.markdown('<a href="#" class="home-button" onclick="window.location.reload()">🏠 Home</a>', unsafe_allow_html=True)
    
    st.title("💡 Study Tips & Strategies")
    
    subjects_topics = get_jamb_subjects_and_topics()
    
    # Random tip of the day
    tip_of_day = StudyTipsSystem.get_random_tip()
    st.markdown(f"""
    <div class="daily-challenge">
        <h3>💡 Tip of the Day</h3>
        <p>{tip_of_day}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Subject-specific tips
    selected_subject = st.selectbox("Select subject for specific tips:", list(subjects_topics.keys()))
    if selected_subject:
        StudyTipsSystem.display_study_tips(selected_subject)

# ─── MAIN APPLICATION CONTROLLER ──────────────────────────────────────────────────
def main():
    """Main application controller"""
    # Initialize systems
    UserManager.initialize_user_data()
    UserManager.update_streak()
    client = initialize_client()
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Route to appropriate page
    if st.session_state.current_page == 'home':
        show_home_page()
    elif st.session_state.current_page == 'subject_selection':
        show_subject_selection()
    elif st.session_state.current_page == 'quiz':
        show_quiz_page(client)
    elif st.session_state.current_page == 'progress':
        show_progress_page()
    elif st.session_state.current_page == 'achievements':
        show_achievements_page()
    elif st.session_state.current_page == 'study_tips':
        show_study_tips_page()

# ─── APPLICATION ENTRY POINT ──────────────────────────────────────────────────────
if __name__ == "__main__":
    main() class="{card_class}">
                    <div class="achievement-icon">{achievement['icon']}</div>
                    <div class="achievement-content">
                        <strong>{achievement['title']}</strong><br>
                        <small>{achievement['description']}</small><br>
                        <span class="points-highlight">+{achievement['xp']} XP</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ─── QUIZ GENERATION SYSTEM ───────────────────────────────────────────────────────
class QuizGenerator:
    @staticmethod
    def generate_questions(client, subject, topic, difficulty="medium", num_questions=5):
        """Generate quiz questions using Gemini AI"""
        try:
            prompt = f"""
            Generate {num_questions} multiple-choice questions for JAMB {subject} on the topic "{topic}".
            Difficulty level: {difficulty}
            
            Format the response as a JSON array with this structure:
            [
                {{
                    "question": "Question text here",
                    "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
                    "correct_answer": "A",
                    "explanation": "Detailed explanation of why this answer is correct"
                }}
            ]
            
            Make sure questions are:
            1. Relevant to JAMB syllabus
            2. Clear and unambiguous
            3. Have exactly 4 options
            4. Include detailed explanations
            """
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[{"role": "user", "parts": [{"text": prompt}]}]
            )
            
            # Parse the JSON response
            questions_data = json.loads(response.text.strip())
            return questions_data
            
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            return []
    
    @staticmethod
    def display_quiz(questions, subject, topic):
        """Display interactive quiz interface"""
        if not questions:
            st.error("No questions available. Please try again.")
            return
        
        st.markdown(f'<div class="quiz-container">', unsafe_allow_html=True)
        st.markdown(f'<span class="subject-badge">{subject}</span>', unsafe_allow_html=True)
        st.subheader(f"Quiz: {topic}")
        
        # Initialize quiz state
        if 'quiz_state' not in st.session_state:
            st.session_state.quiz_state = {
                'current_question': 0,
                'answers': {},
                'start_time': time.time(),
                'submitted': False
            }
        
        current_q = st.session_state.quiz_state['current_question']
        
        # Timer display
        if not st.session_state.quiz_state['submitted']:
            elapsed_time = int(time.time() - st.session_state.quiz_state['start_time'])
            minutes, seconds = divmod(elapsed_time, 60)
            
            timer_class = "timer"
            if elapsed_time > 600:  # 10 minutes
                timer_class += " timer-danger"
            elif elapsed_time > 300:  # 5 minutes
                timer_class += " timer-warning"
            
            st.markdown(f'<div class="{timer_class}">⏱️ Time: {minutes:02d}:{seconds:02d}</div>', unsafe_allow_html=True)
        
        # Question navigation
        progress = (current_q + 1) / len(questions)
        st.progress(progress)
        st.write(f"Question {current_q + 1} of {len(questions)}")
        
        # Display current question
        question_data = questions[current_q]
        st.markdown(f"**{question_data['question']}**")
        
        # Answer options
        answer_key = f"q_{current_q}"
        selected_answer = st.radio(
            "Select your answer:",
            question_data['options'],
            key=f"radio_{current_q}",
            index=None if answer_key not in st.session_state.quiz_state['answers'] else 
                  question_data['options'].index(st.session_state.quiz_state['answers'][answer_key])
        )
        
        if selected_answer:
            st.session_state.quiz_state['answers'][answer_key] = selected_answer
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_q > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.quiz_state['current_question'] -= 1
                    st.rerun()
        
        with col2:
            if current_q < len(questions) - 1:
                if st.button("Next ➡️"):
                    st.session_state.quiz_state['current_question'] += 1
                    st.rerun()
        
        with col3:
            if len(st.session_state.quiz_state['answers']) == len(questions):
                if st.button("Submit Quiz 📝"):
                    QuizGenerator.evaluate_quiz(questions, subject, topic)
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def evaluate_quiz(questions, subject, topic):
        """Evaluate quiz and update user progress"""
        answers = st.session_state.quiz_state['answers']
        correct_count = 0
        
        # Calculate score
        for i, question in enumerate(questions):
            user_answer = answers.get(f"q_{i}", "")
            if user_answer.startswith(question['correct_answer']):
                correct_count += 1
        
        score = (correct_count / len(questions)) * 100
        end_time = time.time()
        duration = int(end_time - st.session_state.quiz_state['start_time'])
        
        # Update user data
        user_data = st.session_state.user_data
        user_data['total_questions_answered'] += len(questions)
        user_data['correct_answers'] += correct_count
        
        # Calculate XP based on performance
        base_xp = len(questions) * 10
        bonus_xp = int(score * 2)  # Bonus based on score
        if duration < 300:  # Speed bonus for under 5 minutes
            bonus_xp += 50
        
        total_xp = base_xp + bonus_xp
        user_data['total_xp'] += total_xp
        user_data['level'] = UserManager.calculate_level(user_data['total_xp'])
        
        # Store quiz result
        quiz_result = {
            'subject': subject,
            'topic': topic,
            'score': score,
            'correct': correct_count,
            'total': len(questions),
            'duration': duration,
            'xp_earned': total_xp,
            'timestamp': datetime.now().isoformat()
        }
        user_data['quiz_history'].append(quiz_result)
        
        # Update subject progress
        if subject not in user_data['subjects_progress']:
            user_data['subjects_progress'][subject] = {'total_quizzes': 0, 'average_score': 0}
        
        subject_progress = user_data['subjects_progress'][subject]
        old_average = subject_progress['average_score']
        old_count = subject_progress['total_quizzes']
        
        subject_progress['average_score'] = (old_average * old_count + score) / (old_count + 1)
        subject_progress['total_quizzes'] += 1
        
        # Check achievements
        AchievementSystem.check_achievements(quiz_result)
        
        # Mark quiz as submitted
        st.session_state.quiz_state['submitted'] = True
        
        # Display results
        QuizGenerator.display_results(questions, quiz_result)
    
    @staticmethod
    def display_results(questions, quiz_result):
        """Display quiz results with detailed feedback"""
        st.markdown(f'<div class="quiz-container">', unsafe_allow_html=True)
        st.subheader("📊 Quiz Results")
        
        # Score display
        score = quiz_result['score']
        if score >= 80:
            st.markdown(f'<div class="success-msg">🎉 Excellent! You scored {score:.1f}%</div>', unsafe_allow_html=True)
        elif score >= 60:
            st.markdown(f'<div class="success-msg">✅ Good job! You scored {score:.1f}%</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-msg">📚 Keep studying! You scored {score:.1f}%</div>', unsafe_allow_html=True)
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Correct Answers", f"{quiz_result['correct']}/{quiz_result['total']}")
        with col2:
            st.metric("Time Taken", f"{quiz_result['duration']//60}:{quiz_result['duration']%60:02d}")
        with col3:
            st.metric("XP Earned", quiz_result['xp_earned'])
        
        # Detailed review
        st.subheader("📝 Answer Review")
        answers = st.session_state.quiz_state['answers']
        
        for i, question in enumerate(questions):
            user_answer = answers.get(f"q_{i}", "")
            is_correct = user_answer.startswith(question['correct_answer'])
            
            with st.expander(f"Question {i+1} {'✅' if is_correct else '❌'}"):
                st.write(f"**Question:** {question['question']}")
                st.write(f"**Your Answer:** {user_answer}")
                st.write(f"**Correct Answer:** {question['correct_answer']}. {question['options'][ord(question['correct_answer']) - ord('A')]}")
                st.write(f"**Explanation:** {question['explanation']}")
        
        # Reset quiz for new attempt
        if st.button("Take Another Quiz"):
            del st.session_state.quiz_state
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ─── PROGRESS TRACKING SYSTEM ─────────────────────────────────────────────────────
class ProgressTracker:
    @staticmethod
    def display_dashboard():
        """Display comprehensive progress dashboard"""
        user_data = st.session_state.user_data
        
        st.subheader("📈 Progress Dashboard")
        
        # User stats card
        level = user_data['level']
        current_xp = user_data['total_xp']
        xp_for_next_level = level * 100
        xp_progress = (current_xp % 100) / 100
        
        st.markdown(f"""
        <div class="stats-card">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="level-badge">{level}</div>
                <div>
                    <h3 style="margin: 0; color: white;">Level {level}</h3>
                    <p style="margin: 0; opacity: 0.9;">{user_data['username'] or 'Student'}</p>
                </div>
            </div>
            <div class="xp-bar">
                <div class="xp-progress" style="width: {xp_progress * 100}%"></div>
            </div>
            <p style="margin-top: 0.5rem; opacity: 0.9;">
                {current_xp % 100} / 100 XP to next level
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Overall statistics
        total_questions = user_data['total_questions_answered']
        correct_answers = user_data['correct_answers']
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total XP", current_xp)
        with col2:
            st.metric("Current Streak", f"{user_data['streak']} days", delta=None)
        with col3:
            st.metric("Questions Answered", total_questions)
        with col4:
            st.metric("Overall Accuracy", f"{accuracy:.1f}%")
        
        # Subject progress
        if user_data['subjects_progress']:
            st.subheader("📚 Subject Mastery")
            for subject, progress in user_data['subjects_progress'].items():
                mastery_percent = min(100, progress['average_score'])
                st.write(f"**{subject}**")
                st.markdown(f"""
                <div
   
