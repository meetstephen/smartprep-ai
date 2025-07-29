# 📘 SmartPrep AI Tutor - JAMB Edition
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent AI-powered tutoring application designed specifically for **JAMB (Joint Admissions and Matriculation Board)** exam preparation. Transform your study experience with gamified learning, personalized progress tracking, and AI-generated practice questions.

![SmartPrep Demo](https://via.placeholder.com/800x400/4f46e5/white?text=SmartPrep+AI+Tutor+Demo)

## ✨ Features

### 🤖 AI-Powered Learning
- **Smart Question Generation**: AI creates unlimited practice questions using Google Gemini
- **Adaptive Difficulty**: Questions adjust to your learning pace
- **Instant Explanations**: Detailed explanations for every answer
- **Real-time Feedback**: Immediate performance evaluation

### 🎮 Gamification System
- **XP Points & Levels**: Earn experience points and level up (1-100 levels)
- **Achievement Badges**: Unlock 7+ different achievements
- **Daily Streaks**: Build consistent study habits with streak tracking
- **Daily Challenges**: Special challenges with bonus rewards

### 📊 Comprehensive Analytics
- **Progress Dashboard**: Visual tracking of your improvement
- **Subject Mastery**: Monitor performance across all JAMB subjects
- **Performance Insights**: Identify strengths and areas for improvement
- **Quiz History**: Detailed records of all your attempts

### 📚 Complete JAMB Coverage
- **6 Core Subjects**: Mathematics, Biology, English, Physics, Chemistry, Government
- **40+ Topics**: Comprehensive coverage of JAMB syllabus
- **Study Tips**: Subject-specific learning strategies
- **Motivational Quotes**: Daily inspiration for your JAMB journey

## 🚀 Quick Start

### Live Demo
Try the app instantly: **[SmartPrep AI Tutor](https://smartprep-ai-tdbleajq7iftomvsfsd5ah.streamlit.app/)**

### Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/smartprep-jamb-tutor.git
cd smartprep-jamb-tutor
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Get your API key**
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key for Gemini

4. **Configure secrets**
```bash
mkdir .streamlit
echo 'GEMINI_API_KEY = "your_api_key_here"' > .streamlit/secrets.toml
```

5. **Run the application**
```bash
streamlit run app.py
```

## 📖 How to Use

### 1. **Create Your Profile** 👤
- Enter your username to start tracking progress
- Your data is automatically saved during your session

### 2. **Take AI-Generated Quizzes** 📝
- Choose from 6 JAMB subjects
- Select specific topics within each subject
- Pick difficulty level (Easy/Medium/Hard)
- Answer 3-10 questions per quiz

### 3. **Track Your Progress** 📈
- Monitor your performance dashboard
- View subject-specific analytics
- Check your quiz history and improvements

### 4. **Unlock Achievements** 🏆
- Complete your first quiz
- Build 7-day and 30-day streaks
- Score perfect marks
- Answer 100+ questions

### 5. **Daily Challenges** 🎯
- Complete special daily challenges
- Earn bonus XP rewards
- Stay motivated with consistent practice

## 🎯 JAMB Subjects Covered

| Subject | Topics Covered | Sample Topics |
|---------|----------------|---------------|
| **Mathematics** | 12 Topics | Algebra, Geometry, Statistics, Calculus |
| **Biology** | 14 Topics | Cell Biology, Genetics, Ecology, Human Anatomy |
| **English Language** | 12 Topics | Comprehension, Grammar, Vocabulary |
| **Physics** | 13 Topics | Mechanics, Electricity, Waves, Modern Physics |
| **Chemistry** | 12 Topics | Organic Chemistry, Atomic Structure, Reactions |
| **Government** | 12 Topics | Nigerian Constitution, Political Systems |

## 🏆 Achievement System

| Achievement | Description | Reward |
|-------------|-------------|---------|
| 🎯 **First Steps** | Complete your first quiz | +50 XP |
| 🔥 **Week Warrior** | Maintain 7-day streak | +100 XP |
| 🏆 **Monthly Master** | Maintain 30-day streak | +500 XP |
| 💯 **Perfectionist** | Score 100% on any quiz | +200 XP |
| ⚡ **Speed Demon** | Complete quiz under 5 minutes | +150 XP |
| 📚 **Knowledge Seeker** | Answer 100+ questions | +300 XP |
| 🎓 **Subject Master** | Achieve 80%+ average in a subject | +400 XP |

## 📱 Screenshots

<details>
<summary>Click to view screenshots</summary>

### Home Dashboard
![Home Dashboard](https://via.placeholder.com/600x400/667eea/white?text=Home+Dashboard)

### Quiz Interface
![Quiz Interface](https://via.placeholder.com/600x400/4f46e5/white?text=Quiz+Interface)

### Progress Tracking
![Progress Tracking](https://via.placeholder.com/600x400/12b886/white?text=Progress+Tracking)

### Achievements
![Achievements](https://via.placeholder.com/600x400/7c3aed/white?text=Achievement+System)

</details>

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS/HTML
- **AI Integration**: Google Gemini API (gemini-2.0-flash)
- **Backend**: Python 3.8+
- **Deployment**: Streamlit Cloud
- **Data Storage**: Session-based (no persistent storage required)

## 📊 Project Stats

- **1000+ Lines of Code**: Comprehensive feature implementation
- **5+ Core Classes**: Modular, maintainable architecture
- **40+ Topics**: Complete JAMB syllabus coverage
- **7+ Achievements**: Gamified learning experience
- **Mobile Responsive**: Works on all devices

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Contribution Ideas
- Add new JAMB subjects or topics
- Improve quiz question quality
- Enhance UI/UX design
- Add new achievement types
- Optimize performance
- Write tests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini API** for AI-powered question generation
- **Streamlit Community** for the excellent framework
- **JAMB** for the standardized curriculum structure
- **Nigerian Students** who inspired this educational tool

## 📞 Support

- **Documentation**: Check our [Deployment Guide](DEPLOYMENT_GUIDE.md)
- **Issues**: Report bugs via [GitHub Issues](https://github.com/meetstephen/smartprep-jamb-tutor/issues)
- **Questions**: Start a [Discussion](https://github.com/meetstephen/smartprep-jamb-tutor/discussions)
- **Email**: meetstephenoyim@gmail.com

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=meetstephen/smartprep-jamb-tutor&type=Date)](https://star-history.com/#meetstephen/smartprep-jamb-tutor&Date)

## 🎓 Educational Impact

**SmartPrep AI Tutor** has been designed to:
- **Improve JAMB Scores**: Targeted practice with instant feedback
- **Build Study Habits**: Gamification encourages consistent learning
- **Identify Weak Areas**: Analytics help focus study efforts
- **Boost Confidence**: Achievement system motivates continuous improvement

---

<div align="center">

**Ready to ace your JAMB exam?** 

[![Try SmartPrep Now](https://smartprep-ai-tdbleajq7iftomvsfsd5ah.streamlit.app/)

*Made with ❤️ for Nigerian students*

</div>

## ⭐ Give us a star!

If SmartPrep AI Tutor helps you in your JAMB preparation, please give us a ⭐ on GitHub. It helps others discover this tool!

---

### 📈 Roadmap

- [ ] **Persistent User Accounts** - Database integration for permanent progress storage
- [ ] **Multiplayer Mode** - Compete with friends in real-time quizzes
- [ ] **Offline Mode** - Download questions for offline practice
- [ ] **Mobile App** - Native iOS and Android applications
- [ ] **Advanced Analytics** - Predictive performance modeling
- [ ] **Social Features** - Study groups and peer learning
- [ ] **Content Expansion** - Additional subjects and question types
