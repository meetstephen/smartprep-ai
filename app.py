import streamlit as st
import google.generativeai as genai
import time
import random
from datetime import datetime, timedelta
import json

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartPrep AI Tutor – JAMB Edition",
    page_icon="📘",
    layout="centered",
)

# ──────────────────────────────────────────────────────────────────────────────
# STYLING
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    :root {
        --primary: #4f46e5;
        --primary-dark: #3730a3;
        --success: #16a34a;
        --danger: #dc2626;
        --warning: #d97706;
        --info: #0ea5e9;
    }
    .main-header {text-align:center;margin-bottom:1.5rem}
    .nav-bar {
        background:linear-gradient(135deg,#667eea,#764ba2);
        padding:0.8rem 1.2rem;border-radius:0.75rem;margin-bottom:1.2rem;
        display:flex;justify-content:space-between;align-items:center;color:#fff;
        flex-wrap:wrap;gap:0.5rem;
    }
    .nav-title {font-size:1.3rem;font-weight:700}
    .nav-stats {display:flex;gap:0.6rem;font-size:0.85rem;flex-wrap:wrap}
    .nav-stats span {background:rgba(255,255,255,.2);padding:0.2rem 0.6rem;border-radius:1rem}
    .quiz-box {
        background:#f8f9fa;padding:1.5rem;border-radius:1rem;margin:1rem 0;
        box-shadow:0 4px 12px rgba(0,0,0,.08);
    }
    .msg-success {
        background:linear-gradient(135deg,#d1fae5,#a7f3d0);color:#065f46;
        padding:1rem;border-radius:0.5rem;margin:0.75rem 0;text-align:center;
        border-left:4px solid var(--success);font-weight:600;
    }
    .msg-error {
        background:linear-gradient(135deg,#fee2e2,#fecaca);color:#991b1b;
        padding:1rem;border-radius:0.5rem;margin:0.75rem 0;text-align:center;
        border-left:4px solid var(--danger);font-weight:600;
    }
    .msg-info {
        background:linear-gradient(135deg,#e0f2fe,#bae6fd);color:#0c4a6e;
        padding:1rem;border-radius:0.5rem;margin:0.75rem 0;
        border-left:4px solid var(--info);
    }
    .msg-warn {
        background:linear-gradient(135deg,#fef9c3,#fde68a);color:#92400e;
        padding:1rem;border-radius:0.5rem;margin:0.75rem 0;
        border-left:4px solid var(--warning);
    }
    .timer {
        background:linear-gradient(135deg,#e0f2fe,#bae6fd);color:#0369a1;
        padding:0.6rem;border-radius:0.5rem;text-align:center;
        font-size:1.2rem;font-weight:700;margin:0.4rem 0;
    }
    .timer-warn {background:linear-gradient(135deg,#fef9c3,#fde68a);color:#92400e}
    .timer-danger {
        background:linear-gradient(135deg,#fee2e2,#fecaca);color:#991b1b;
        animation:pulse 1s infinite;
    }
    @keyframes pulse {
        0%,100%{opacity:1;transform:scale(1)}
        50%{opacity:.8;transform:scale(1.01)}
    }
    .badge {
        display:inline-block;background:linear-gradient(135deg,#4f46e5,#7c3aed);
        color:#fff;padding:0.15rem 0.6rem;border-radius:1rem;font-size:0.8rem;
        margin-right:0.4rem;margin-bottom:0.3rem;
    }
    .stat-card {
        background:linear-gradient(135deg,#f0f9ff,#e0f2fe);padding:1.2rem;
        border-radius:0.75rem;margin-bottom:0.75rem;border-left:4px solid var(--primary);
    }
    .xp-bar {height:0.6rem;background:#e5e7eb;border-radius:0.3rem;margin-top:0.4rem;overflow:hidden}
    .xp-fill {height:100%;background:linear-gradient(90deg,#4f46e5,#7c3aed);border-radius:0.3rem;transition:width .5s}
    .mastery-bar {height:0.45rem;background:#e5e7eb;border-radius:0.25rem;margin:0.3rem 0;overflow:hidden}
    .mastery-fill {height:100%;background:linear-gradient(90deg,#059669,#34d399);border-radius:0.25rem;transition:width .5s}
    .achievement {
        background:#f8f9fa;padding:0.8rem;border-radius:0.6rem;margin-bottom:0.6rem;
        border:1px solid #e5e7eb;display:flex;align-items:center;gap:0.8rem;
    }
    .achievement.locked {filter:grayscale(1);opacity:.55}
    .level-circle {
        display:inline-flex;align-items:center;justify-content:center;
        background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;
        font-weight:700;width:2.2rem;height:2.2rem;border-radius:50%;font-size:0.95rem;
    }
    .question-num-indicator {
        font-size: 0.85rem; color: #6b7280; margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# BUILT-IN JAMB QUESTION BANK  (offline fallback + supplement)
# ──────────────────────────────────────────────────────────────────────────────
JAMB_QUESTION_BANK = {
    "Mathematics": [
        {"question": "If log₁₀2 = 0.3010, find log₁₀8.", "options": ["A) 0.6020", "B) 0.9030", "C) 2.4030", "D) 1.2040"], "answer": "B", "explanation": "8 = 2³, so log₁₀8 = 3 × log₁₀2 = 3 × 0.3010 = 0.9030.", "topic": "Algebra and Equations", "difficulty": "Medium"},
        {"question": "Convert 101101₂ to base 10.", "options": ["A) 45", "B) 53", "C) 44", "D) 46"], "answer": "A", "explanation": "1×2⁵+0×2⁴+1×2³+1×2²+0×2¹+1×2⁰ = 32+0+8+4+0+1 = 45.", "topic": "Number Bases", "difficulty": "Easy"},
        {"question": "Solve 2x² + 5x − 3 = 0.", "options": ["A) x = ½ or x = −3", "B) x = −½ or x = 3", "C) x = 1 or x = −3", "D) x = 3 or x = ½"], "answer": "A", "explanation": "Factoring: (2x − 1)(x + 3) = 0 ⇒ x = ½ or x = −3.", "topic": "Algebra and Equations", "difficulty": "Medium"},
        {"question": "A fair die is thrown twice. What is the probability of getting a sum of 7?", "options": ["A) 1/12", "B) 1/6", "C) 5/36", "D) 7/36"], "answer": "B", "explanation": "Favourable outcomes: (1,6),(2,5),(3,4),(4,3),(5,2),(6,1) = 6 out of 36. P = 6/36 = 1/6.", "topic": "Statistics and Probability", "difficulty": "Medium"},
        {"question": "Find dy/dx if y = 3x³ − 2x² + x − 5.", "options": ["A) 9x² − 4x + 1", "B) 9x² − 4x − 1", "C) 9x² + 4x + 1", "D) 3x² − 2x + 1"], "answer": "A", "explanation": "Differentiating term by term: dy/dx = 9x² − 4x + 1.", "topic": "Calculus", "difficulty": "Medium"},
        {"question": "If A = {1,2,3,4,5} and B = {3,4,5,6,7}, find A ∩ B.", "options": ["A) {1,2}", "B) {3,4,5}", "C) {6,7}", "D) {1,2,3,4,5,6,7}"], "answer": "B", "explanation": "The intersection contains elements common to both sets: {3, 4, 5}.", "topic": "Sets and Logic", "difficulty": "Easy"},
        {"question": "Simplify (√50 − √32) / √2.", "options": ["A) 1", "B) √2", "C) 3", "D) 2"], "answer": "A", "explanation": "√50 = 5√2, √32 = 4√2. So (5√2 − 4√2)/√2 = √2/√2 = 1.", "topic": "Algebra and Equations", "difficulty": "Medium"},
        {"question": "Find the determinant of the matrix [[2, 3],[4, 1]].", "options": ["A) −10", "B) 10", "C) −14", "D) 14"], "answer": "A", "explanation": "det = (2×1) − (3×4) = 2 − 12 = −10.", "topic": "Matrices", "difficulty": "Medium"},
        {"question": "The 3rd term of a G.P. is 18 and the 6th term is 486. Find the first term.", "options": ["A) 2", "B) 3", "C) 6", "D) 9"], "answer": "A", "explanation": "ar² = 18, ar⁵ = 486. Dividing: r³ = 27, r = 3. Then a(9) = 18, a = 2.", "topic": "Algebra and Equations", "difficulty": "Hard"},
        {"question": "Find the distance between points P(3, −2) and Q(−1, 1).", "options": ["A) 5", "B) 4", "C) 7", "D) √13"], "answer": "A", "explanation": "d = √[(3−(−1))² + (−2−1)²] = √[16+9] = √25 = 5.", "topic": "Geometry and Trigonometry", "difficulty": "Easy"},
    ],
    "English Language": [
        {"question": "Choose the word that best completes the sentence: The teacher asked the students to ______ their essays before submission.", "options": ["A) revise", "B) devise", "C) advise", "D) supervise"], "answer": "A", "explanation": "'Revise' means to re-examine and make corrections, which is what students do to essays before submission.", "topic": "Lexis and Structure", "difficulty": "Easy"},
        {"question": "Select the option that best explains the idiom: 'to bury the hatchet'.", "options": ["A) To start a fight", "B) To make peace", "C) To hide a weapon", "D) To dig a grave"], "answer": "B", "explanation": "'Bury the hatchet' is an idiom meaning to end a conflict and make peace.", "topic": "Figurative Expressions", "difficulty": "Medium"},
        {"question": "Identify the figure of speech in: 'The wind howled through the night.'", "options": ["A) Simile", "B) Metaphor", "C) Personification", "D) Hyperbole"], "answer": "C", "explanation": "Attributing the human action of 'howling' to wind is personification.", "topic": "Literary Devices", "difficulty": "Easy"},
        {"question": "Choose the correct option: Neither the students nor the teacher ______ present.", "options": ["A) were", "B) was", "C) are", "D) have been"], "answer": "B", "explanation": "With 'neither…nor', the verb agrees with the nearest subject ('teacher' = singular), so 'was'.", "topic": "Grammatical Structures", "difficulty": "Medium"},
        {"question": "Which of these words is a synonym of 'benevolent'?", "options": ["A) Malicious", "B) Kind", "C) Wealthy", "D) Intelligent"], "answer": "B", "explanation": "'Benevolent' means well-meaning and kindly, synonymous with 'kind'.", "topic": "Synonyms and Antonyms", "difficulty": "Easy"},
        {"question": "The expression 'a red herring' means:", "options": ["A) A type of fish", "B) A misleading clue", "C) A dangerous situation", "D) An embarrassing moment"], "answer": "B", "explanation": "A 'red herring' is something that misleads or distracts from a relevant issue.", "topic": "Figurative Expressions", "difficulty": "Medium"},
        {"question": "Choose the word with the correct stress pattern (capitalised syllable): PHOTOGRAPH", "options": ["A) phoTOgraph", "B) PHOtograph", "C) photoGRAPH", "D) phoTOGraph"], "answer": "B", "explanation": "The stress in 'photograph' falls on the first syllable: PHO-to-graph.", "topic": "Oral Forms", "difficulty": "Medium"},
        {"question": "Identify the sentence with correct punctuation:", "options": ["A) Its a beautiful day isnt it?", "B) It's a beautiful day, isn't it?", "C) Its a beautiful day, isn't it?", "D) It's a beautiful day isnt it."], "answer": "B", "explanation": "'It's' (contraction) and 'isn't it?' (tag question) both need apostrophes, and a comma separates the tag.", "topic": "Grammatical Structures", "difficulty": "Easy"},
    ],
    "Physics": [
        {"question": "A body of mass 5 kg is moving with a velocity of 10 m/s. What is its kinetic energy?", "options": ["A) 50 J", "B) 100 J", "C) 250 J", "D) 500 J"], "answer": "C", "explanation": "KE = ½mv² = ½ × 5 × 10² = ½ × 5 × 100 = 250 J.", "topic": "Mechanics", "difficulty": "Easy"},
        {"question": "A wire of resistance 6Ω is drawn out so that its length is doubled. What is the new resistance?", "options": ["A) 3Ω", "B) 6Ω", "C) 12Ω", "D) 24Ω"], "answer": "D", "explanation": "When length doubles, area halves (volume constant). R = ρL/A → new R = ρ(2L)/(A/2) = 4ρL/A = 4×6 = 24Ω.", "topic": "Electricity and Magnetism", "difficulty": "Hard"},
        {"question": "Which of the following is a vector quantity?", "options": ["A) Speed", "B) Temperature", "C) Momentum", "D) Energy"], "answer": "C", "explanation": "Momentum has both magnitude and direction, making it a vector. Speed, temperature, and energy are scalars.", "topic": "Mechanics", "difficulty": "Easy"},
        {"question": "The image formed by a plane mirror is:", "options": ["A) Real and inverted", "B) Virtual and erect", "C) Real and erect", "D) Virtual and inverted"], "answer": "B", "explanation": "A plane mirror always produces a virtual, erect, and laterally inverted image of the same size.", "topic": "Optics", "difficulty": "Easy"},
        {"question": "A sound wave has a frequency of 340 Hz and travels at 340 m/s. What is its wavelength?", "options": ["A) 0.5 m", "B) 1.0 m", "C) 2.0 m", "D) 340 m"], "answer": "B", "explanation": "λ = v/f = 340/340 = 1.0 m.", "topic": "Waves", "difficulty": "Medium"},
        {"question": "The half-life of a radioactive substance is 4 days. What fraction remains after 12 days?", "options": ["A) 1/4", "B) 1/8", "C) 1/16", "D) 1/2"], "answer": "B", "explanation": "12 days = 3 half-lives. Fraction remaining = (½)³ = 1/8.", "topic": "Nuclear Physics", "difficulty": "Medium"},
        {"question": "An object is thrown vertically upward with a velocity of 20 m/s. What is the maximum height reached? (g = 10 m/s²)", "options": ["A) 10 m", "B) 20 m", "C) 40 m", "D) 80 m"], "answer": "B", "explanation": "At max height v = 0. Using v² = u² − 2gh: 0 = 400 − 20h → h = 20 m.", "topic": "Mechanics", "difficulty": "Medium"},
    ],
    "Chemistry": [
        {"question": "What is the IUPAC name of CH₃CH₂OH?", "options": ["A) Methanol", "B) Ethanol", "C) Propanol", "D) Butanol"], "answer": "B", "explanation": "CH₃CH₂OH has 2 carbon atoms with an -OH group, making it ethanol.", "topic": "Organic Chemistry", "difficulty": "Easy"},
        {"question": "Which of the following is a strong electrolyte?", "options": ["A) CH₃COOH", "B) NH₃", "C) NaCl", "D) C₂H₅OH"], "answer": "C", "explanation": "NaCl (sodium chloride) completely dissociates in water, making it a strong electrolyte.", "topic": "Electrochemistry", "difficulty": "Medium"},
        {"question": "In the periodic table, elements in the same group have the same:", "options": ["A) Atomic mass", "B) Number of electron shells", "C) Number of valence electrons", "D) Atomic number"], "answer": "C", "explanation": "Elements in the same group have the same number of valence (outermost) electrons, giving them similar chemical properties.", "topic": "Atomic Structure", "difficulty": "Easy"},
        {"question": "The pH of a neutral solution at 25°C is:", "options": ["A) 0", "B) 1", "C) 7", "D) 14"], "answer": "C", "explanation": "At 25°C, a neutral solution has equal concentrations of H⁺ and OH⁻, giving pH = 7.", "topic": "Acids and Bases", "difficulty": "Easy"},
        {"question": "What type of bond is formed between Na and Cl in NaCl?", "options": ["A) Covalent", "B) Metallic", "C) Ionic", "D) Van der Waals"], "answer": "C", "explanation": "Na donates an electron to Cl, forming Na⁺ and Cl⁻ ions held together by electrostatic (ionic) bonding.", "topic": "Chemical Bonding", "difficulty": "Easy"},
        {"question": "Which gas is produced when dilute HCl reacts with Na₂CO₃?", "options": ["A) Hydrogen", "B) Oxygen", "C) Carbon dioxide", "D) Chlorine"], "answer": "C", "explanation": "Na₂CO₃ + 2HCl → 2NaCl + H₂O + CO₂. Carbon dioxide gas is liberated.", "topic": "Chemical Reactions", "difficulty": "Medium"},
        {"question": "Le Chatelier's principle states that when a system at equilibrium is disturbed, it:", "options": ["A) Stops reacting", "B) Shifts to oppose the change", "C) Shifts to reinforce the change", "D) Reaches a new equilibrium immediately"], "answer": "B", "explanation": "Le Chatelier's principle: a system at equilibrium shifts in the direction that tends to counteract the imposed change.", "topic": "Physical Chemistry", "difficulty": "Medium"},
    ],
    "Biology": [
        {"question": "The organelle responsible for protein synthesis in a cell is the:", "options": ["A) Mitochondrion", "B) Ribosome", "C) Golgi apparatus", "D) Lysosome"], "answer": "B", "explanation": "Ribosomes are the sites of protein synthesis, translating mRNA into polypeptide chains.", "topic": "Cell Biology", "difficulty": "Easy"},
        {"question": "In Mendel's experiment, if Tt is crossed with Tt, what is the phenotypic ratio?", "options": ["A) 1:1", "B) 1:2:1", "C) 3:1", "D) 2:1"], "answer": "C", "explanation": "Tt × Tt gives TT:Tt:tt = 1:2:1 genotypically, but 3 tall : 1 short phenotypically (3:1).", "topic": "Genetics", "difficulty": "Medium"},
        {"question": "Malaria is caused by:", "options": ["A) Virus", "B) Bacteria", "C) Plasmodium", "D) Trypanosoma"], "answer": "C", "explanation": "Malaria is caused by Plasmodium parasites (P. falciparum, P. vivax, etc.) transmitted by female Anopheles mosquitoes.", "topic": "Microbiology", "difficulty": "Easy"},
        {"question": "The part of the flower that develops into a fruit after fertilisation is the:", "options": ["A) Sepal", "B) Petal", "C) Ovary", "D) Anther"], "answer": "C", "explanation": "After fertilisation, the ovary of the flower develops into the fruit, enclosing the seeds.", "topic": "Plant Biology", "difficulty": "Easy"},
        {"question": "Which blood group is the universal donor?", "options": ["A) A", "B) B", "C) AB", "D) O"], "answer": "D", "explanation": "Blood group O has no A or B antigens on red blood cells, so it can be donated to all ABO groups (universal donor).", "topic": "Human Anatomy and Physiology", "difficulty": "Easy"},
        {"question": "The process by which green plants manufacture food using sunlight is called:", "options": ["A) Respiration", "B) Transpiration", "C) Photosynthesis", "D) Osmosis"], "answer": "C", "explanation": "Photosynthesis is the process by which plants use light energy, CO₂, and water to produce glucose and oxygen.", "topic": "Plant Biology", "difficulty": "Easy"},
        {"question": "In an ecosystem, organisms that feed on dead organic matter are called:", "options": ["A) Producers", "B) Primary consumers", "C) Decomposers", "D) Tertiary consumers"], "answer": "C", "explanation": "Decomposers (e.g., bacteria and fungi) break down dead organic matter and recycle nutrients.", "topic": "Ecology", "difficulty": "Easy"},
        {"question": "Sickle cell anaemia is caused by a mutation in the gene coding for:", "options": ["A) Insulin", "B) Haemoglobin", "C) Keratin", "D) Collagen"], "answer": "B", "explanation": "Sickle cell anaemia results from a point mutation in the haemoglobin gene (HBB), producing abnormal haemoglobin S.", "topic": "Genetics", "difficulty": "Medium"},
    ],
    "Government": [
        {"question": "The 1999 Constitution of Nigeria provides for a:", "options": ["A) Parliamentary system", "B) Confederate system", "C) Presidential system", "D) Monarchical system"], "answer": "C", "explanation": "Nigeria's 1999 Constitution establishes a presidential system with separation of powers among the executive, legislature, and judiciary.", "topic": "Nigerian Constitution", "difficulty": "Easy"},
        {"question": "The principle of separation of powers was advocated by:", "options": ["A) John Locke", "B) Montesquieu", "C) Jean-Jacques Rousseau", "D) Thomas Hobbes"], "answer": "B", "explanation": "Baron de Montesquieu articulated the doctrine of separation of powers into executive, legislative, and judicial branches.", "topic": "Political Parties", "difficulty": "Medium"},
        {"question": "INEC stands for:", "options": ["A) Independent National Electoral Council", "B) Independent National Electoral Commission", "C) Internal National Electoral Commission", "D) Independent Nigerian Electoral Committee"], "answer": "B", "explanation": "INEC is the Independent National Electoral Commission, responsible for conducting elections in Nigeria.", "topic": "Electoral Systems", "difficulty": "Easy"},
        {"question": "How many geo-political zones does Nigeria have?", "options": ["A) 4", "B) 5", "C) 6", "D) 7"], "answer": "C", "explanation": "Nigeria has 6 geo-political zones: North-Central, North-East, North-West, South-East, South-South, and South-West.", "topic": "Nigerian Federalism", "difficulty": "Easy"},
        {"question": "The highest court in Nigeria is the:", "options": ["A) Court of Appeal", "B) Federal High Court", "C) Supreme Court", "D) High Court"], "answer": "C", "explanation": "The Supreme Court is the apex court in Nigeria and the final court of appeal.", "topic": "Nigerian Political System", "difficulty": "Easy"},
    ],
    "Economics": [
        {"question": "The law of demand states that, ceteris paribus, as price increases:", "options": ["A) Quantity demanded increases", "B) Quantity demanded decreases", "C) Supply increases", "D) Supply decreases"], "answer": "B", "explanation": "The law of demand: price and quantity demanded are inversely related, all other factors held constant.", "topic": "Microeconomics", "difficulty": "Easy"},
        {"question": "GDP stands for:", "options": ["A) General Domestic Price", "B) Gross Domestic Product", "C) General Development Plan", "D) Gross Development Product"], "answer": "B", "explanation": "GDP (Gross Domestic Product) is the total monetary value of all finished goods and services produced within a country's borders.", "topic": "Macroeconomics", "difficulty": "Easy"},
        {"question": "An increase in supply, with demand unchanged, leads to:", "options": ["A) Higher equilibrium price", "B) Lower equilibrium price", "C) No change in price", "D) Higher demand"], "answer": "B", "explanation": "When supply increases (shifts right) with constant demand, the equilibrium price falls and quantity rises.", "topic": "Microeconomics", "difficulty": "Medium"},
        {"question": "Which of the following is NOT a function of the Central Bank of Nigeria?", "options": ["A) Issuing currency", "B) Banker to commercial banks", "C) Accepting deposits from individuals", "D) Controlling monetary policy"], "answer": "C", "explanation": "The CBN does not accept deposits from the general public; that is the role of commercial banks.", "topic": "Monetary Economics", "difficulty": "Medium"},
        {"question": "Inflation is best described as:", "options": ["A) A fall in the general price level", "B) A persistent rise in the general price level", "C) An increase in the value of money", "D) A decrease in production"], "answer": "B", "explanation": "Inflation is a sustained increase in the general level of prices for goods and services over time.", "topic": "Macroeconomics", "difficulty": "Easy"},
    ],
}

# ──────────────────────────────────────────────────────────────────────────────
# JAMB SUBJECTS & CURRICULUM TOPICS
# ──────────────────────────────────────────────────────────────────────────────
JAMB_SUBJECTS = {
    "Mathematics": {
        "icon": "🔢",
        "topics": ["Algebra and Equations", "Geometry and Trigonometry", "Statistics and Probability",
                   "Calculus", "Vectors", "Matrices", "Number Bases", "Sets and Logic"],
        "desc": "Algebra, Geometry, Calculus, Statistics & more",
    },
    "English Language": {
        "icon": "📝",
        "topics": ["Comprehension", "Lexis and Structure", "Oral Forms", "Figurative Expressions",
                   "Literary Devices", "Registers", "Synonyms and Antonyms", "Grammatical Structures"],
        "desc": "Grammar, Comprehension & Language Skills",
    },
    "Biology": {
        "icon": "🧬",
        "topics": ["Cell Biology", "Genetics", "Ecology", "Evolution", "Plant Biology",
                   "Animal Biology", "Human Anatomy and Physiology", "Microbiology",
                   "Reproduction", "Nutrition"],
        "desc": "Life Sciences, Genetics & Anatomy",
    },
    "Physics": {
        "icon": "⚛️",
        "topics": ["Mechanics", "Energy", "Waves", "Optics", "Electricity and Magnetism",
                   "Modern Physics", "Heat and Temperature", "Electronics", "Nuclear Physics"],
        "desc": "Mechanics, Waves, Electricity & Modern Physics",
    },
    "Chemistry": {
        "icon": "🧪",
        "topics": ["Atomic Structure", "Chemical Bonding", "Chemical Reactions", "Acids and Bases",
                   "Organic Chemistry", "Physical Chemistry", "Inorganic Chemistry", "Electrochemistry"],
        "desc": "Atoms, Bonding, Reactions & Organic Chemistry",
    },
    "Government": {
        "icon": "🏛️",
        "topics": ["Nigerian Constitution", "Nigerian Political System", "Nigerian Federalism",
                   "Political Parties", "Electoral Systems", "Public Administration",
                   "Nigerian Foreign Policy", "International Relations"],
        "desc": "Nigerian Politics, Constitution & Governance",
    },
    "Literature in English": {
        "icon": "📚",
        "topics": ["Drama", "Poetry", "Prose", "Literary Terms", "African Literature",
                   "Non-African Literature", "Literary Criticism", "Literary History"],
        "desc": "Drama, Poetry, Prose & Literary Analysis",
    },
    "Economics": {
        "icon": "💰",
        "topics": ["Microeconomics", "Macroeconomics", "Development Economics", "Public Finance",
                   "International Economics", "Monetary Economics", "Nigerian Economy", "Economic Theory"],
        "desc": "Micro/Macro Economics & Nigerian Economy",
    },
    "Geography": {
        "icon": "🌍",
        "topics": ["Physical Geography", "Human Geography", "Regional Geography", "Map Reading",
                   "Environmental Geography", "Economic Geography", "Population Geography", "Climatology"],
        "desc": "Physical & Human Geography, Map Reading",
    },
    "Agricultural Science": {
        "icon": "🌾",
        "topics": ["Soil Science", "Crop Production", "Animal Production", "Agricultural Economics",
                   "Farm Mechanization", "Agricultural Ecology", "Fisheries", "Forestry"],
        "desc": "Crop & Animal Production, Soil Science",
    },
    "Accounting": {
        "icon": "📊",
        "topics": ["Financial Accounting", "Cost Accounting", "Principles of Accounting", "Bookkeeping",
                   "Financial Statements", "Partnership Accounting", "Company Accounting",
                   "Public Sector Accounting"],
        "desc": "Financial Accounting & Bookkeeping",
    },
    "Commerce": {
        "icon": "🏢",
        "topics": ["Trade", "Business Organizations", "Marketing", "Money and Banking",
                   "Insurance", "Stock Exchange", "Communication", "Consumer Protection"],
        "desc": "Trade, Marketing & Business Organizations",
    },
    "Christian Religious Studies": {
        "icon": "✝️",
        "topics": ["The Bible", "Old Testament", "New Testament", "Church History",
                   "Christian Ethics", "Christian Doctrines", "Christian Living"],
        "desc": "Bible Study & Christian Teachings",
    },
    "Islamic Studies": {
        "icon": "☪️",
        "topics": ["Qur'an", "Hadith", "Tawhid", "Fiqh", "Islamic History",
                   "Islamic Ethics", "Islamic Civilization"],
        "desc": "Qur'an, Hadith & Islamic Principles",
    },
    "Computer Science": {
        "icon": "💻",
        "topics": ["Computer Fundamentals", "Programming", "Data Processing", "Database",
                   "Computer Networks", "Information Systems", "Software Development"],
        "desc": "Programming, Databases & IT Systems",
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# API INITIALISATION (with robust fallback)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def init_model():
    """Initialise Gemini with a fallback chain of model IDs."""
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return None

    genai.configure(api_key=api_key)

    model_ids = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]
    for mid in model_ids:
        try:
            model = genai.GenerativeModel(mid)
            model.generate_content("Say OK")
            return model
        except Exception:
            continue

    return None


def get_model():
    """Return the cached model or None."""
    return init_model()


# ──────────────────────────────────────────────────────────────────────────────
# QUESTION GENERATION
# ──────────────────────────────────────────────────────────────────────────────
def pick_topic(subject, used_topics):
    """Pick a topic that hasn't been used yet (if possible)."""
    topics = JAMB_SUBJECTS[subject]["topics"]
    available = [t for t in topics if t not in used_topics]
    return random.choice(available) if available else random.choice(topics)


def generate_ai_question(model, subject, topic, difficulty):
    """Call Gemini to generate a single JAMB-style MCQ."""
    prompt = f"""You are a JAMB exam question setter for Nigeria's Unified Tertiary Matriculation Examination.

Create ONE {difficulty.lower()}-level multiple-choice question for **{subject}** on the topic **{topic}**.

Rules:
- Follow the official JAMB/WAEC curriculum for Senior Secondary School.
- Use Nigerian context where appropriate (examples, names, geography).
- Test understanding, not rote memorisation.
- Distractors should reflect common student misconceptions.
- Provide a thorough explanation referencing the underlying principle.

Respond in EXACTLY this format (no extra text):
Question: <question text>
A) <option>
B) <option>
C) <option>
D) <option>
Answer: <letter only, e.g. B>
Explanation: <detailed explanation>
Topic: {topic}"""

    try:
        resp = model.generate_content(prompt)
        return parse_ai_response(resp.text.strip(), topic)
    except Exception:
        return None


def parse_ai_response(text, fallback_topic="General"):
    """Parse the structured AI response into a dict."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    q, opts, ans, expl, topic = "", [], "", "", fallback_topic
    for line in lines:
        if line.lower().startswith("question:"):
            q = line.split(":", 1)[1].strip()
        elif line[:2] in ("A)", "B)", "C)", "D)"):
            opts.append(line)
        elif line.lower().startswith("answer:"):
            ans = line.split(":", 1)[1].strip()[:1]
        elif line.lower().startswith("explanation:"):
            expl = line.split(":", 1)[1].strip()
        elif line.lower().startswith("topic:"):
            topic = line.split(":", 1)[1].strip()
    if q and len(opts) >= 4 and ans and expl:
        return {"question": q, "options": opts[:4], "answer": ans,
                "explanation": expl, "topic": topic, "source": "ai"}
    return None


def get_bank_question(subject, difficulty, used_hashes):
    """Pull a question from the built-in bank that hasn't been shown yet."""
    bank = JAMB_QUESTION_BANK.get(subject, [])
    candidates = [q for q in bank
                  if q.get("difficulty", "Medium") == difficulty
                  and hash(q["question"]) not in used_hashes]
    if not candidates:
        candidates = [q for q in bank if hash(q["question"]) not in used_hashes]
    if not candidates:
        candidates = bank
    if candidates:
        chosen = random.choice(candidates)
        chosen["source"] = "bank"
        return chosen
    return None


def get_question(model, subject, difficulty, used_topics, used_hashes):
    """Get a question: try AI first, fall back to bank."""
    topic = pick_topic(subject, used_topics)

    if model:
        q = generate_ai_question(model, subject, topic, difficulty)
        if q and hash(q["question"]) not in used_hashes:
            return q

    return get_bank_question(subject, difficulty, used_hashes)


# ──────────────────────────────────────────────────────────────────────────────
# GAMIFICATION HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def calc_xp(score, total, difficulty, time_efficiency=1.0):
    base = 50
    score_xp = int((score / max(total, 1)) * 200)
    time_bonus = int(time_efficiency * 50)
    mult = {"Easy": 1.0, "Medium": 1.25, "Hard": 1.5}.get(difficulty, 1.0)
    return int((base + score_xp + time_bonus) * mult)


def level_from_xp(xp):
    return 1 + xp // 500


def xp_progress_pct(xp):
    lvl = level_from_xp(xp)
    lo = (lvl - 1) * 500
    hi = lvl * 500
    return int(((xp - lo) / (hi - lo)) * 100)


def update_streak(last_date_str, current_streak):
    today = datetime.now().date()
    if not last_date_str:
        return 1, today.isoformat()
    if isinstance(last_date_str, str):
        last = datetime.strptime(last_date_str, "%Y-%m-%d").date()
    else:
        last = last_date_str
    diff = (today - last).days
    if diff == 0:
        return current_streak, last_date_str
    elif diff == 1:
        return current_streak + 1, today.isoformat()
    else:
        return 1, today.isoformat()


ACHIEVEMENTS_DEF = [
    ("first_quiz", "🎯", "First Steps", "Complete your first quiz", lambda d: d["quizzes"] >= 1),
    ("five_quizzes", "🏅", "Quiz Enthusiast", "Complete 5 quizzes", lambda d: d["quizzes"] >= 5),
    ("twenty_quizzes", "🏆", "Quiz Master", "Complete 20 quizzes", lambda d: d["quizzes"] >= 20),
    ("first_perfect", "💯", "Perfect Start", "Score 100% on a quiz", lambda d: d["perfects"] >= 1),
    ("five_perfect", "🌟", "Excellence", "Score 100% on 5 quizzes", lambda d: d["perfects"] >= 5),
    ("streak_3", "🔥", "On Fire", "3-day study streak", lambda d: d["streak"] >= 3),
    ("streak_7", "🔥🔥", "Weekly Warrior", "7-day study streak", lambda d: d["streak"] >= 7),
    ("streak_30", "🔥🔥🔥", "Dedication", "30-day study streak", lambda d: d["streak"] >= 30),
    ("multi_subj", "📚", "Renaissance Learner", "Practice 3+ subjects", lambda d: d["subjects_tried"] >= 3),
    ("speed_demon", "⚡", "Speed Demon", "Finish a quiz with >80% time left", lambda d: d.get("fast_finish", False)),
]


def get_unlocked(data):
    return [a for a in ACHIEVEMENTS_DEF if a[4](data)]


# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ──────────────────────────────────────────────────────────────────────────────
DEFAULTS = {
    "stage": "home",
    "mode": "quick",
    "subject": "Mathematics",
    "difficulty": "Medium",
    "time_per_q": 120,
    "total_qs": 10,
    "questions": [],
    "answers": [],
    "current_idx": 0,
    "show_feedback": False,
    "timer_start": None,
    "total_time": 0.0,
    "timer_expired": False,
    "confirm_home": False,
    "xp": 0,
    "quizzes_done": 0,
    "perfects": 0,
    "streak": 1,
    "last_date": datetime.now().date().isoformat(),
    "history": {},
    "unlocked_ids": [],
    "cbt_subjects": [],
    "cbt_per_subject": 10,
}


def init_state():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ──────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def nav_bar():
    lvl = level_from_xp(st.session_state.xp)
    st.markdown(f"""<div class="nav-bar">
        <div class="nav-title">📘 SmartPrep AI</div>
        <div class="nav-stats">
            <span>Lvl {lvl}</span>
            <span>{st.session_state.xp} XP</span>
            <span>🔥 {st.session_state.streak}</span>
            <span>📊 {st.session_state.quizzes_done}</span>
        </div>
    </div>""", unsafe_allow_html=True)


def home_btn():
    if st.session_state.stage != "home":
        if st.button("🏠 Home", key="nav_home"):
            st.session_state.confirm_home = True


def handle_home_confirm():
    if st.session_state.get("confirm_home"):
        st.warning("⚠️ Return home? Your current quiz progress will be lost.")
        c1, c2, _ = st.columns([1, 1, 2])
        with c1:
            if st.button("✅ Yes", key="confirm_y"):
                reset_quiz()
                st.session_state.stage = "home"
                st.session_state.confirm_home = False
                st.rerun()
        with c2:
            if st.button("❌ No", key="confirm_n"):
                st.session_state.confirm_home = False
                st.rerun()


def reset_quiz():
    for k in ["questions", "answers", "current_idx", "show_feedback",
              "timer_start", "total_time", "timer_expired", "confirm_home",
              "cbt_subjects"]:
        st.session_state[k] = DEFAULTS[k]


def fmt_time(s):
    m, s = divmod(int(s), 60)
    return f"{m:02d}:{s:02d}"


def timer_cls(secs):
    if secs < 30:
        return "timer timer-danger"
    if secs < 60:
        return "timer timer-warn"
    return "timer"


# ──────────────────────────────────────────────────────────────────────────────
# HOME SCREEN
# ──────────────────────────────────────────────────────────────────────────────
def show_home():
    st.markdown("""<div class="main-header">
        <h1 style="color:#4f46e5">📘 SmartPrep AI Tutor — JAMB Edition</h1>
        <p style="color:#6b7280">AI-powered preparation for JAMB UTME success</p>
    </div>""", unsafe_allow_html=True)

    model = get_model()
    if model is None:
        st.markdown('<div class="msg-warn">⚠️ AI is unavailable — using built-in JAMB past question bank. '
                    'To enable AI questions, add <code>GEMINI_API_KEY</code> in Streamlit secrets.</div>',
                    unsafe_allow_html=True)

    if st.session_state.quizzes_done > 0:
        show_stats_summary()

    st.markdown("---")
    st.markdown("### 🎮 Choose Your Study Mode")

    mode_cols = st.columns(3)
    with mode_cols[0]:
        st.markdown('<div class="quiz-box" style="text-align:center">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Quick Quiz")
        st.markdown("10 questions · 1 subject · Timed")
        if st.button("Start Quick Quiz", key="mode_quick", use_container_width=True):
            st.session_state.mode = "quick"
        st.markdown("</div>", unsafe_allow_html=True)

    with mode_cols[1]:
        st.markdown('<div class="quiz-box" style="text-align:center">', unsafe_allow_html=True)
        st.markdown("#### 🖥️ CBT Simulation")
        st.markdown("Multi-subject · JAMB-style · Full exam feel")
        if st.button("Start CBT Sim", key="mode_cbt", use_container_width=True):
            st.session_state.mode = "cbt"
        st.markdown("</div>", unsafe_allow_html=True)

    with mode_cols[2]:
        st.markdown('<div class="quiz-box" style="text-align:center">', unsafe_allow_html=True)
        st.markdown("#### 🎯 Topic Focus")
        st.markdown("Drill a specific topic · No time limit")
        if st.button("Start Topic Focus", key="mode_topic", use_container_width=True):
            st.session_state.mode = "topic"
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    mode = st.session_state.mode
    mode_labels = {"quick": "Quick Quiz", "cbt": "CBT Simulation", "topic": "Topic Focus"}
    st.markdown(f"### ⚙️ Configure: **{mode_labels[mode]}**")

    if mode == "quick":
        configure_quick()
    elif mode == "cbt":
        configure_cbt()
    else:
        configure_topic()

    if st.session_state.history:
        show_recommendations()


def configure_quick():
    c1, c2 = st.columns(2)
    with c1:
        subj = st.selectbox("Subject", list(JAMB_SUBJECTS.keys()),
                            format_func=lambda s: f"{JAMB_SUBJECTS[s]['icon']} {s}", key="sel_subj")
        st.markdown(f'<div class="msg-info">{JAMB_SUBJECTS[subj]["desc"]}</div>', unsafe_allow_html=True)
    with c2:
        diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="sel_diff")
        time_opt = st.selectbox("Time per question",
                                ["60s", "90s", "2 min (recommended)", "3 min", "No limit"],
                                index=2, key="sel_time")
    time_map = {"60s": 60, "90s": 90, "2 min (recommended)": 120, "3 min": 180, "No limit": None}

    if st.button("🚀 Begin Quiz", type="primary", use_container_width=True, key="start_quick"):
        st.session_state.subject = subj
        st.session_state.difficulty = diff
        st.session_state.time_per_q = time_map[time_opt]
        st.session_state.total_qs = 10
        launch_quiz([subj])


def configure_cbt():
    st.markdown("Select **4 subjects** (like real JAMB UTME):")
    all_subjs = list(JAMB_SUBJECTS.keys())
    chosen = st.multiselect("Subjects", all_subjs,
                            default=["English Language", "Mathematics"],
                            max_selections=4, key="cbt_pick")
    diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="cbt_diff")
    qs_per = st.slider("Questions per subject", 5, 60, 15, 5, key="cbt_qs")

    if len(chosen) < 2:
        st.info("Select at least 2 subjects to start.")
    else:
        total = len(chosen) * qs_per
        total_time = total * 1.5
        st.markdown(f"**Total: {total} questions · ~{int(total_time)} min**")
        if st.button("🚀 Begin CBT Simulation", type="primary", use_container_width=True, key="start_cbt"):
            st.session_state.difficulty = diff
            st.session_state.time_per_q = 90
            st.session_state.total_qs = total
            st.session_state.cbt_subjects = chosen
            st.session_state.cbt_per_subject = qs_per
            launch_quiz(chosen)


def configure_topic():
    subj = st.selectbox("Subject", list(JAMB_SUBJECTS.keys()),
                        format_func=lambda s: f"{JAMB_SUBJECTS[s]['icon']} {s}", key="tp_subj")
    topics = JAMB_SUBJECTS[subj]["topics"]
    topic = st.selectbox("Topic", topics, key="tp_topic")
    diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="tp_diff")
    n_qs = st.slider("Number of questions", 5, 20, 10, key="tp_nqs")

    if st.button("🚀 Begin Topic Drill", type="primary", use_container_width=True, key="start_topic"):
        st.session_state.subject = subj
        st.session_state.difficulty = diff
        st.session_state.time_per_q = None
        st.session_state.total_qs = n_qs
        st.session_state._forced_topic = topic
        launch_quiz([subj])


def launch_quiz(subjects):
    """Generate the first question and transition to quiz stage."""
    reset_quiz()
    model = get_model()
    subj = subjects[0] if len(subjects) == 1 else random.choice(subjects)
    forced_topic = st.session_state.get("_forced_topic", None)

    if forced_topic:
        topic = forced_topic
    else:
        topic = pick_topic(subj, [])

    st.session_state.subject = subj

    with st.spinner("🔄 Generating your first question..."):
        q = get_question(model, subj, st.session_state.difficulty, [topic], set())

    if q:
        q["_subject"] = subj
        st.session_state.questions = [q]
        st.session_state.answers = [None]
        st.session_state.current_idx = 0
        st.session_state.timer_start = time.time() if st.session_state.time_per_q else None
        st.session_state.stage = "quiz"
        st.rerun()
    else:
        st.error("Could not generate a question. Please check your internet connection or try another subject.")


# ──────────────────────────────────────────────────────────────────────────────
# QUIZ SCREEN
# ──────────────────────────────────────────────────────────────────────────────
def show_quiz():
    model = get_model()
    idx = st.session_state.current_idx
    total = st.session_state.total_qs
    q = st.session_state.questions[idx]

    # Timer
    if st.session_state.time_per_q and st.session_state.timer_start and not st.session_state.show_feedback:
        elapsed = time.time() - st.session_state.timer_start
        left = max(0, st.session_state.time_per_q - elapsed)
        cls = timer_cls(left)
        st.markdown(f'<div class="{cls}">⏱️ {fmt_time(left)}</div>', unsafe_allow_html=True)
        if left <= 0 and not st.session_state.timer_expired:
            st.session_state.timer_expired = True
            st.session_state.show_feedback = True
            st.session_state.answers[idx] = "__EXPIRED__"
            record_answer(q, False)
            st.rerun()

    # Progress
    answered_count = sum(1 for a in st.session_state.answers if a is not None)
    score = sum(1 for i, a in enumerate(st.session_state.answers)
                if a and a != "__EXPIRED__" and a.startswith(st.session_state.questions[i]["answer"]))
    pct = (idx + 1) / total
    st.progress(pct)
    subj_display = q.get("_subject", st.session_state.subject)
    st.markdown(f'<span class="badge">{subj_display}</span> '
                f'<span class="question-num-indicator">Question {idx+1} of {total} · '
                f'Score: {score}/{answered_count}</span>',
                unsafe_allow_html=True)

    # Question
    st.markdown('<div class="quiz-box">', unsafe_allow_html=True)
    st.markdown(f"**Topic:** {q.get('topic', 'General')} · **Difficulty:** {st.session_state.difficulty}")
    st.markdown(f"### {q['question']}")

    if not st.session_state.show_feedback:
        choice = st.radio("Select your answer:", q["options"], key=f"choice_{idx}")
        if st.button("✅ Submit Answer", type="primary", use_container_width=True, key=f"submit_{idx}"):
            st.session_state.answers[idx] = choice
            if st.session_state.timer_start:
                st.session_state.total_time += time.time() - st.session_state.timer_start
            is_correct = choice.startswith(q["answer"])
            record_answer(q, is_correct)
            st.session_state.show_feedback = True
            st.rerun()
    else:
        user_ans = st.session_state.answers[idx]
        correct_letter = q["answer"]

        if user_ans == "__EXPIRED__":
            st.markdown(f'<div class="msg-error">⏰ Time expired! Correct answer: <b>{correct_letter}</b></div>',
                        unsafe_allow_html=True)
        elif user_ans and user_ans.startswith(correct_letter):
            st.markdown('<div class="msg-success">✅ Correct! Well done! 🎉</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-error">❌ Incorrect. Correct answer: <b>{correct_letter}</b></div>',
                        unsafe_allow_html=True)

        st.markdown("#### 💡 Explanation")
        st.markdown(f'<div class="msg-info">{q["explanation"]}</div>', unsafe_allow_html=True)

        # Navigation
        if idx + 1 >= total:
            if st.button("🎯 View Results", type="primary", use_container_width=True, key="to_results"):
                st.session_state.stage = "results"
                st.rerun()
        else:
            if st.button("➡️ Next Question", type="primary", use_container_width=True, key="next_q"):
                advance_question(model)

    st.markdown("</div>", unsafe_allow_html=True)


def record_answer(q, is_correct):
    """Record to subject history."""
    subj = q.get("_subject", st.session_state.subject)
    if subj not in st.session_state.history:
        st.session_state.history[subj] = []
    st.session_state.history[subj].append({
        "topic": q.get("topic", "General"),
        "correct": is_correct,
        "difficulty": st.session_state.difficulty,
        "date": datetime.now().isoformat(),
    })


def advance_question(model):
    """Generate and load the next question."""
    idx = st.session_state.current_idx + 1
    used_topics = [q.get("topic", "") for q in st.session_state.questions]
    used_hashes = {hash(q["question"]) for q in st.session_state.questions}

    # For CBT mode, cycle through subjects
    if st.session_state.cbt_subjects:
        subjs = st.session_state.cbt_subjects
        per = st.session_state.cbt_per_subject
        subj_idx = idx // per if per > 0 else 0
        subj_idx = min(subj_idx, len(subjs) - 1)
        subj = subjs[subj_idx]
    else:
        subj = st.session_state.subject

    with st.spinner("🔄 Generating next question..."):
        q = get_question(model, subj, st.session_state.difficulty, used_topics, used_hashes)

    if q:
        q["_subject"] = subj
        st.session_state.questions.append(q)
        st.session_state.answers.append(None)
        st.session_state.current_idx = idx
        st.session_state.show_feedback = False
        st.session_state.timer_expired = False
        st.session_state.timer_start = time.time() if st.session_state.time_per_q else None
        st.rerun()
    else:
        st.error("Failed to generate next question. Please try again.")


# ──────────────────────────────────────────────────────────────────────────────
# RESULTS SCREEN
# ──────────────────────────────────────────────────────────────────────────────
def show_results():
    st.balloons()
    qs = st.session_state.questions
    ans = st.session_state.answers
    total = len(qs)
    score = sum(1 for i in range(total)
                if ans[i] and ans[i] != "__EXPIRED__" and ans[i].startswith(qs[i]["answer"]))
    pct = (score / max(total, 1)) * 100

    # XP
    time_eff = max(0, 1 - (st.session_state.total_time / max(total * 120, 1))) if st.session_state.total_time > 0 else 1
    xp_earned = calc_xp(score, total, st.session_state.difficulty, time_eff)
    old_lvl = level_from_xp(st.session_state.xp)
    st.session_state.xp += xp_earned
    st.session_state.quizzes_done += 1
    if score == total:
        st.session_state.perfects += 1
    new_lvl = level_from_xp(st.session_state.xp)
    st.session_state.streak, st.session_state.last_date = update_streak(
        st.session_state.last_date, st.session_state.streak)

    st.markdown('<div class="quiz-box">', unsafe_allow_html=True)

    if new_lvl > old_lvl:
        st.markdown(f'<div class="msg-success">🎉 LEVEL UP! You reached Level {new_lvl}! 🚀</div>',
                    unsafe_allow_html=True)

    st.markdown("## 🎉 Quiz Complete!")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Score", f"{score}/{total}", f"{pct:.0f}%")
    with c2:
        if st.session_state.total_time > 0:
            st.metric("Time", f"{st.session_state.total_time/60:.1f} min")
        else:
            st.metric("Time", "Untimed")
    with c3:
        st.metric("XP Earned", f"+{xp_earned}")
    with c4:
        st.metric("Level", new_lvl)

    # Performance message
    if pct == 100:
        st.markdown('<div class="msg-success">🌟 PERFECT SCORE! You\'re JAMB-ready! 🏆</div>', unsafe_allow_html=True)
    elif pct >= 80:
        st.markdown('<div class="msg-success">🌟 Excellent! Keep this momentum going! 👏</div>', unsafe_allow_html=True)
    elif pct >= 60:
        st.markdown('<div class="msg-info">👍 Good effort! A little more practice and you\'ll ace it! 💪</div>', unsafe_allow_html=True)
    elif pct >= 40:
        st.markdown('<div class="msg-warn">📖 Review the explanations below and try again. You\'re improving!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="msg-warn">📚 Focus on the explanations and study the weak topics. You\'ve got this!</div>', unsafe_allow_html=True)

    # XP bar
    prog = xp_progress_pct(st.session_state.xp)
    st.markdown(f'<span class="level-circle">{new_lvl}</span> **Level {new_lvl}** — {st.session_state.xp} XP total',
                unsafe_allow_html=True)
    st.markdown(f'<div class="xp-bar"><div class="xp-fill" style="width:{prog}%"></div></div>', unsafe_allow_html=True)
    st.markdown(f"**{prog}%** to Level {new_lvl + 1}")

    # Achievements
    ach_data = {
        "quizzes": st.session_state.quizzes_done,
        "perfects": st.session_state.perfects,
        "streak": st.session_state.streak,
        "subjects_tried": len(st.session_state.history),
        "fast_finish": time_eff > 0.8,
    }
    newly_unlocked = [a for a in get_unlocked(ach_data) if a[0] not in st.session_state.unlocked_ids]
    if newly_unlocked:
        st.markdown("### 🏆 New Achievements!")
        for aid, icon, title, desc, _ in newly_unlocked:
            st.markdown(f'<div class="achievement"><span style="font-size:1.8rem">{icon}</span>'
                        f'<div><b>{title}</b><br>{desc}</div></div>', unsafe_allow_html=True)
            st.session_state.unlocked_ids.append(aid)

    # Detailed question review
    st.markdown("---")
    st.markdown("### 📋 Question-by-Question Review")
    for i, (q, a) in enumerate(zip(qs, ans)):
        subj_label = q.get("_subject", st.session_state.subject)
        is_correct = a and a != "__EXPIRED__" and a.startswith(q["answer"])
        icon = "✅" if is_correct else ("⏰" if a == "__EXPIRED__" else "❌")
        with st.expander(f"{icon} Q{i+1}: {q['question'][:80]}... ({subj_label} — {q.get('topic','')})"):
            if a == "__EXPIRED__":
                st.markdown("**Your answer:** Time expired")
            else:
                st.markdown(f"**Your answer:** {a}")
            st.markdown(f"**Correct answer:** {q['answer']}")
            st.markdown(f"**Explanation:** {q['explanation']}")

    # Topic mastery breakdown
    st.markdown("---")
    st.markdown("### 📈 Topic Performance This Quiz")
    topic_stats = {}
    for i, q in enumerate(qs):
        t = q.get("topic", "General")
        if t not in topic_stats:
            topic_stats[t] = {"correct": 0, "total": 0}
        topic_stats[t]["total"] += 1
        if ans[i] and ans[i] != "__EXPIRED__" and ans[i].startswith(q["answer"]):
            topic_stats[t]["correct"] += 1

    for topic, data in sorted(topic_stats.items(), key=lambda x: x[1]["correct"] / max(x[1]["total"], 1)):
        m = int((data["correct"] / max(data["total"], 1)) * 100)
        if m >= 70:
            colour = "#059669"
        elif m >= 40:
            colour = "#d97706"
        else:
            colour = "#dc2626"
        st.markdown(f"**{topic}** — {data['correct']}/{data['total']} ({m}%)")
        st.markdown(f'<div class="mastery-bar"><div class="mastery-fill" style="width:{m}%;background:{colour}"></div></div>',
                    unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Actions
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 New Quiz", type="primary", use_container_width=True, key="new_quiz"):
            reset_quiz()
            st.session_state.stage = "home"
            st.rerun()
    with c2:
        if st.button("🔁 Retry Same Subject", use_container_width=True, key="retry"):
            launch_quiz([st.session_state.subject])


# ──────────────────────────────────────────────────────────────────────────────
# STATS & RECOMMENDATIONS
# ──────────────────────────────────────────────────────────────────────────────
def show_stats_summary():
    lvl = level_from_xp(st.session_state.xp)
    prog = xp_progress_pct(st.session_state.xp)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<span class="level-circle">{lvl}</span> **Level {lvl}** · {st.session_state.xp} XP',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="xp-bar"><div class="xp-fill" style="width:{prog}%"></div></div>',
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f"**📊 Quizzes:** {st.session_state.quizzes_done} · "
                    f"**💯 Perfects:** {st.session_state.perfects}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        streak_label = "days" if st.session_state.streak != 1 else "day"
        st.markdown(f"**🔥 Streak:** {st.session_state.streak} {streak_label}")
        st.markdown("</div>", unsafe_allow_html=True)


def show_recommendations():
    """Identify weak topics and suggest study focus."""
    weak = []
    for subj, entries in st.session_state.history.items():
        topic_map = {}
        for e in entries:
            t = e["topic"]
            if t not in topic_map:
                topic_map[t] = {"c": 0, "t": 0}
            topic_map[t]["t"] += 1
            if e["correct"]:
                topic_map[t]["c"] += 1
        for t, d in topic_map.items():
            mastery = d["c"] / max(d["t"], 1)
            if mastery < 0.5 and d["t"] >= 2:
                weak.append((subj, t, int(mastery * 100), d["t"]))

    if weak:
        weak.sort(key=lambda x: x[2])
        st.markdown("### 🎯 Recommended Focus Areas")
        st.markdown('<div class="msg-warn">These topics need more practice based on your history:</div>',
                    unsafe_allow_html=True)
        for subj, topic, mastery, attempts in weak[:5]:
            st.markdown(f"- **{subj} → {topic}** — {mastery}% mastery ({attempts} attempts)")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    init_state()

    if st.session_state.stage != "home":
        nav_bar()
        home_btn()
        handle_home_confirm()

    if st.session_state.stage == "home":
        show_home()
    elif st.session_state.stage == "quiz":
        show_quiz()
    elif st.session_state.stage == "results":
        show_results()


if __name__ == "__main__":
    main()
