import streamlit as st
import sqlite3

# ---------- Analyze Weak Units ----------
def analyze_weak_units():
    weak = {}

    for attempt in st.session_state.quiz_history:
        percent = attempt["score"] / attempt["total"]

        if percent < 0.7:  # below 70% = weak
            subject = attempt["subject"]
            unit = attempt["unit"]

            if subject not in weak:
                weak[subject] = []

            if unit not in weak[subject]:
                weak[subject].append(unit)

    return weak


# ---------- Study Tips ----------
def get_study_tips(unit):
    tips = {
        "Unit 1": (
            "🔴 You are struggling with foundational algebra skills.\n"
            "• Review linear equations and inequalities\n"
            "• Practice solving equations step by step\n"
            "• Focus on understanding slope and intercept form\n"
            "• Use 10–15 practice problems per day"
        ),

        "Unit 2": (
            "🔴 You are having trouble with functions and their graphs.\n"
            "• Review function notation (f(x))\n"
            "• Practice identifying domain and range\n"
            "• Work on graph transformations (shifts, stretches, reflections)\n"
            "• Re-draw graphs by hand to build intuition"
        ),

        "Unit 3": (
            "🔴 You are struggling with polynomial and rational functions.\n"
            "• Review factoring techniques\n"
            "• Practice polynomial division\n"
            "• Focus on zeros, end behavior, and asymptotes\n"
            "• Rework missed quiz questions carefully"
        ),

        "Unit 4": (
            "🔴 You are having difficulty with advanced modeling and applications.\n"
            "• Slow down on word problems and underline key info\n"
            "• Practice setting up equations before solving\n"
            "• Review past homework and quizzes\n"
            "• Explain problems out loud to check understanding"
        ),
    }

    return tips.get(unit, "Review class notes and redo missed problems.")


# ---------- Session State Defaults ----------
if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []

if "quiz_results" not in st.session_state:
    st.session_state.quiz_results = []

if "quiz_scores" not in st.session_state:
    st.session_state.quiz_scores = {}

if "show_questions" not in st.session_state:
    st.session_state.show_questions = False

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="EduSphere",
    page_icon="🎓",
    layout="wide"
)

# =============================
# STYLES
# =============================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a1a3c, #2b124f);
    color: white;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.08);
    border-radius: 25px;
    padding: 12px 20px;
    margin-right: 8px;
    color: white;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #9333ea);
}
.stButton>button {
    border-radius: 30px;
    background: linear-gradient(135deg, #4f46e5, #9333ea);
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =============================
# DATABASE
# =============================
conn = sqlite3.connect("gpa_users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS grades (
    course TEXT,
    section TEXT,
    semester1 REAL,
    semester2 REAL,
    q1 REAL,
    q2 REAL,
    q3 REAL,
    q4 REAL,
    gt_year TEXT
)
""")
conn.commit()

# =============================
# HELPERS
# =============================
def weighted_gpa(avg, weight):
    return max(weight - ((100 - avg) * 0.1), 0)

def unweighted_gpa(avg):
    if avg >= 90: return 4
    if avg >= 80: return 3
    if avg >= 70: return 2
    if avg >= 60: return 1
    return 0

# =============================
# COURSES
# =============================
courses = {
    "Spanish 1": 5.0,
    "Spanish 2": 5.0,
    "Spanish 3": 5.5,
    "Spanish 4 AP": 6.0,
    "Algebra 1": 5.5,
    "Geometry": 5.5,
    "Algebra 2": 5.5,
    "AP Precalculus": 6.0,
    "GT / AP World History": {1: 5.5, 2: 6.0},
    "Biology": 5.5,
    "Chemistry": 5.5,
    "AP Human Geography": 6.0,
    "Sports": 5.0,
    "Health": 5.0,
    "Computer Science": 5.5,
    "AP Computer Science": 6.0,
    "Instruments": 5.0
}

# =============================
# MAIN APP
# =============================
st.title("🎓 EduSphere")

main_tabs = st.tabs(["🏠 Welcome", "🎓 GPA", "📝 Quiz & Practice", "📅 Organization Helper"])

# =============================
# WELCOME TAB
# =============================
with main_tabs[0]:
    st.subheader("Welcome to EduSphere!")
    st.write(
        "Hey! I created this app/website for YOU to have a convenient way to track your educational path. "
        "There is no platform (until now) which allows you to get your cumulative GPA, and that was the inspiration for this. "
        "Throughout this app, you can track your GPA, analyze it, and practice quizzes to improve your learning! "
        "Additionally, you do not need to give any personal credentials; you just manually input your grades and no one (including me) will have access to your personal information and grades."
    )
    st.image(
        "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=800&q=80",
        use_column_width=True
    )

# =============================
# GPA TAB
# =============================
with main_tabs[1]:
    st.header("📊 GPA Calculator")

    st.markdown(
        """
        <div style="text-align: center; margin-left: 50px;">
            <img src="https://images.unsplash.com/photo-1519452575417-564c1401ecc0?auto=format&fit=crop&w=900&q=80" width="200">
        </div>
        """,
        unsafe_allow_html=True
    )

    sub_tabs = st.tabs(["🏫 Middle School", "🎓 High School", "📊 GPA & Analytics"])

    # =============================
    # MIDDLE SCHOOL
    # =============================
    with sub_tabs[0]:
        st.header("Middle School Grades")

        ms_selected = st.multiselect(
            "Select the courses you took (MS)",
            options=list(courses.keys()),
            key="ms_courses"
        )

        ms_course_grades = {}
        for course in ms_selected:
            s1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, key=f"ms_s1_{course}")
            s2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, key=f"ms_s2_{course}")
            ms_course_grades[course] = (s1, s2)

            gt_year = None
            if course == "GT / AP World History":
                year = st.selectbox(f"Select year for {course}:", [1, 2], key=f"{course}_year")
                weight = courses[course][year]
            else:
                weight = courses[course]

            c.execute("""
            INSERT OR REPLACE INTO grades VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                course, "MS", s1, s2, None, None, None, None, gt_year
            ))
        conn.commit()

    # =============================
    # HIGH SCHOOL
    # =============================
    with sub_tabs[1]:
        st.header("High School Grades")

        hs_selected = st.multiselect(
            "Select the courses you took (HS)",
            options=list(courses.keys()),
            key="hs_courses"
        )

        hs_course_grades = {}
        for course in hs_selected:
            quarters = st.slider(f"Quarters Completed – {course}", 1, 4, 2, key=f"hs_quarters_{course}")
            q_grades = []
            for i in range(quarters):
                q_grades.append(st.number_input(f"{course} – Quarter {i+1}", 0.0, 100.0, key=f"hs_q{i+1}_{course}"))
            hs_course_grades[course] = q_grades

            gt_year = None
            if course == "GT / AP World History":
                year = st.selectbox(f"Select year for {course}:", [1, 2], key=f"{course}_year")
                weight = courses[course][year]
            else:
                weight = courses[course]

            padded = q_grades + [None] * (4 - len(q_grades))
            c.execute("""
            INSERT OR REPLACE INTO grades VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                course, "HS", None, None, *padded, gt_year
            ))
        conn.commit()

    # =============================
    # GPA & Analytics
    # =============================
    with sub_tabs[2]:
        st.header("GPA Results & Analytics")
        if st.button("🎯 Calculate GPA"):
            weighted, unweighted = [], []

            # Middle School
            for course, (s1, s2) in ms_course_grades.items():
                avg = (s1 + s2) / 2
                weight = courses.get(course, 5.0)
                weighted.append(weighted_gpa(avg, weight))
                unweighted.append(unweighted_gpa(avg))

            # High School
            for course, grades in hs_course_grades.items():
                avg = sum(grades) / len(grades)
                weight = courses.get(course, 5.0)
                weighted.append(weighted_gpa(avg, weight))
                unweighted.append(unweighted_gpa(avg))

            if not weighted:
                st.warning("No courses selected.")
            else:
                w = round(sum(weighted)/len(weighted),2)
                uw = round(sum(unweighted)/len(unweighted),2)
                st.success(f"🎓 Weighted GPA: {w}")
                st.success(f"📘 Unweighted GPA: {uw}")

                st.subheader("📊 GPA Insight")
                if w >= 5.5:
                    st.write("Your GPA is being boosted by strong performance in weighted courses.")
                elif w >= 4.5:
                    st.write("Your GPA is solid, but higher-weight classes have the biggest impact.")
                else:
                    st.write("Lower performance in GPA-heavy courses is pulling your GPA down.")

# =============================
# QUIZ TAB
# =============================
with main_tabs[2]:
    unit = None
    difficulty = None

    st.subheader("Quiz & Practice Problems")

    # Create sub-tabs for each subject
    quiz_subjects = ["Spanish", "Math"]
    quiz_tabs = st.tabs(quiz_subjects)

    # =============================
    # SPANISH QUIZ
    # =============================
    with quiz_tabs[0]:
        st.header("Spanish Quiz")
        spanish_level = st.selectbox("Select your Spanish level:",
                                     ["Spanish 1", "Spanish 2", "Spanish 3", "Spanish 4 AP"])

        if spanish_level == "Spanish 1":
            q1 = st.radio("Select the correct translation: 'I eat an apple.'",
                          ["Yo como una manzana", "Yo comer una manzana", "Yo comí una manzana"])
            q2 = st.radio("Select the correct verb conjugation: 'Tú (hablar) español.'", ["hablas", "hablo", "habla"])
        elif spanish_level == "Spanish 2":
            q1 = st.radio("Select the correct past tense: 'He ate lunch.'",
                          ["Él comió almuerzo", "Él comer almuerzo", "Él comía almuerzo"])
            q2 = st.radio("Choose correct subjunctive: 'Es importante que tú (estudiar) para el examen.'",
                          ["estudies", "estudias", "estudiar"])
        elif spanish_level == "Spanish 3":
            q1 = st.radio("Choose the correct conditional: 'I would travel to Spain.'",
                          ["Yo viajaría a España", "Yo viajaré a España", "Yo viajo a España"])
            q2 = st.radio("Select correct past perfect: 'I had eaten before school.'",
                          ["Había comido antes de la escuela", "He comido antes de la escuela",
                           "Comí antes de la escuela"])
        else:
            q1 = st.radio("Select the correct subjunctive past: 'It was necessary that he had finished.'",
                          ["Era necesario que él hubiera terminado", "Era necesario que él terminó",
                           "Era necesario que él había terminado"])
            q2 = st.radio("Select correct idiomatic expression: 'To be over the moon.'",
                          ["Estar en la luna", "Estar en el cielo", "Tener la luna"])
        st.success("Spanish quiz section loaded. Answers are not yet auto-graded.")

    # =============================
    # MATH QUIZ
    # =============================
    with quiz_tabs[1]:
        st.header("AP Precalculus Quiz")

# Full Precalculus Questions for Units 1-4
        questions = {

                "Unit 1": {
                    "Easy": [
                        {"type": "mcq", "question": "Solve for x: x^2 - 5x + 6 = 0",
                         "options": ["x=2 or 3", "x=1 or 6", "x=0 or 6"], "answer": "x=2 or 3"},
                        {"type": "text", "question": "Find the zeros of f(x) = x^2 - 4", "answer": "2,-2"},
                        {"type": "mcq", "question": "Simplify: (x^2 - 9)/(x+3)", "options": [ "x+3", "x-3","x^2+3"],
                         "answer": "x-3"},
                        {"type": "text", "question": "Determine if f(x)= -x^2 + 2x + 3 has a maximum or minimum",
                         "answer": "maximum"},
                        {"type": "mcq", "question": "Find f(2) if f(x)=x^2+3x-1", "options": ["9", "7", "5"],
                         "answer": "7"},
                        {"type": "mcq", "question": "Which is a vertical asymptote of f(x)=1/(x-5)?",
                         "options": [ "x=-5", "x=0", "x=5"], "answer": "x=5"},
                        {"type": "text", "question": "Find the average rate of change of f(x)=x^2 from x=1 to x=4",
                         "answer": "7"},
                        {"type": "text", "question": "Factor completely: x^3 - 3x^2 - 4x + 12",
                         "answer": "(x-2)(x-2)(x+3)"},
                        {"type": "mcq", "question": "Identify the leading coefficient of f(x)=3x^4-2x^3+5",
                         "options": [ "-2", "3", "5"], "answer": "3"},
                        {"type": "text", "question": "Solve for x: (x^2+2x)/(x^2-4) > 0",
                         "answer": "x<-2 or x>0 and x!=2"},
                        {"type": "mcq", "question": "What is f(0) for f(x)=2x^2-3x+1?", "options": [ "0", "1", "-1"],
                         "answer": "1"},
                        {"type": "text", "question": "Find the x-intercepts of f(x)=x^2-6x+8", "answer": "2,4"}
                    ],
                    "Medium": [
                        {"type": "mcq", "question": "Divide: (2x^3+3x^2-x+5)/(x+2)",
                         "options": ["2x^2-x+3", "2x^2+7x+15", "2x^2-x+1"], "answer": "2x^2-x+3"},
                        {"type": "text", "question": "Factor completely: x^3 - 3x^2 - 4x + 12",
                         "answer": "(x-2)(x-2)(x+3)"},
                        {"type": "mcq", "question": "Which is a vertical asymptote of f(x)=1/(x-5)?",
                         "options": ["x=5", "x=-5", "x=0"], "answer": "x=5"},
                        {"type": "text", "question": "Find the average rate of change of f(x)=x^2 from x=1 to x=4",
                         "answer": "7"},
                        {"type": "mcq", "question": "Identify the leading coefficient of f(x)=3x^4-2x^3+5",
                         "options": ["3", "-2", "5"], "answer": "3"},
                        {"type": "text", "question": "Solve: x^3 - 6x^2 + 11x - 6 = 0", "answer": "1,2,3"},
                        {"type": "mcq", "question": "Simplify: (x^3 - 8)/(x-2)",
                         "options": ["x^2+2x+4", "x^2-2x+4", "x^2+4"], "answer": "x^2+2x+4"},
                        {"type": "text", "question": "Find f'(x) for f(x)=x^3-5x^2+6x", "answer": "3x^2-10x+6"},
                        {"type": "mcq", "question": "End behavior of f(x)=-2x^4+3x^2",
                         "options": ["f→-∞ as x→∞", "f→∞ as x→∞", "f→0 as x→∞"], "answer": "f→-∞ as x→∞"},
                        {"type": "text", "question": "Solve for x: (x^2-1)/(x+1) < 0", "answer": "x<-1 or 0<x<1"},
                        {"type": "mcq", "question": "Find f(-1) if f(x)=x^2-2x+3", "options": ["6", "4", "3"],
                         "answer": "6"},
                        {"type": "text", "question": "Determine if f(x)=x^2-4x+3 opens up or down", "answer": "up"}
                    ],
                    "Hard": [
                        {"type": "text", "question": "Find all real solutions for x: 2x^4 - 3x^3 - 11x^2 + 6x + 9 = 0",
                         "answer": "-1,1,3/2,-1/2"},
                        {"type": "mcq", "question": "If f(x)=(x^2-4)/(x^2-9), holes in the graph?",
                         "options": ["None", "x=2", "x=3"], "answer": "None"},
                        {"type": "text", "question": "Find the rate of change at x=2 for f(x)=x^3 - 2x^2 + x",
                         "answer": "7"},
                        {"type": "mcq", "question": "End behavior of f(x)=-x^3+4x^2",
                         "options": ["As x→∞, f(x)→ -∞", "As x→∞, f(x)→ ∞", "As x→∞, f(x)→ 0"],
                         "answer": "As x→∞, f(x)→ -∞"},
                        {"type": "text", "question": "Solve for x: (x^2+2x)/(x^2-4) > 0",
                         "answer": "x<-2 or x>0 and x!=2"},
                        {"type": "text", "question": "Find all zeros of f(x)=x^4-5x^2+4", "answer": "1,-1,2,-2"},
                        {"type": "mcq", "question": "Simplify: (x^3+27)/(x+3)",
                         "options": ["x^2-3x+9", "x^2+3x+9", "x^2-3x-9"], "answer": "x^2-3x+9"},
                        {"type": "text", "question": "Determine the vertex of f(x)=-2x^2+4x+1", "answer": "(1,3)"},
                        {"type": "mcq", "question": "Which is the horizontal asymptote of f(x)=(2x^2+3)/(x^2+1)",
                         "options": ["y=2", "y=0", "y=3"], "answer": "y=2"},
                        {"type": "text", "question": "Solve: x^3-6x^2+11x-6=0", "answer": "1,2,3"},
                        {"type": "mcq", "question": "Find f(1) for f(x)=2x^3-3x^2+1", "options": ["0", "1", "2"],
                         "answer": "0"},
                        {"type": "text", "question": "Factor: x^3-7x^2+10x", "answer": "x(x-5)(x-2)"}
                    ]
                },
                "Unit 2": {
                    "Easy": [
                        {"type": "mcq", "question": "Simplify: (x^2-16)/(x-4)", "options": ["x+4", "x-4", "x^2+4"],
                         "answer": "x+4"},
                        {"type": "text", "question": "Find the zeros of f(x)=x^2-5x+6", "answer": "2,3"},
                        {"type": "mcq", "question": "Evaluate f(2) if f(x)=x^2+2x", "options": ["6", "8", "4"],
                         "answer": "6"},
                        {"type": "text", "question": "Factor: x^2+5x+6", "answer": "(x+2)(x+3)"},
                        {"type": "mcq", "question": "Which is a vertical asymptote of f(x)=1/(x-3)?",
                         "options": ["x=3", "x=-3", "x=0"], "answer": "x=3"},
                        {"type": "text", "question": "Determine the vertex of f(x)=x^2-4x+1", "answer": "(2,-3)"},
                        {"type": "mcq", "question": "Find f(0) if f(x)=x^2-3x+2", "options": ["2", "0", "-2"],
                         "answer": "2"},
                        {"type": "text", "question": "Find the average rate of change of f(x)=x^2 from x=0 to x=2",
                         "answer": "2"},
                        {"type": "mcq", "question": "Simplify: (x^2-25)/(x+5)", "options": ["x-5", "x+5", "x^2+5"],
                         "answer": "x-5"},
                        {"type": "text", "question": "Solve x^2-9=0", "answer": "3,-3"},
                        {"type": "mcq", "question": "Find f(-1) if f(x)=x^2+2x+1", "options": ["0", "2", "-1"],
                         "answer": "0"},
                        {"type": "text", "question": "Determine if f(x)=-x^2+2x+3 opens up or down", "answer": "down"}
                    ],
                    "Medium": [
                        {"type": "mcq", "question": "Divide: (x^3-2x^2+3x-4)/(x-1)",
                         "options": ["x^2-x+2", "x^2+x+4", "x^2-x+1"], "answer": "x^2-x+2"},
                        {"type": "text", "question": "Factor completely: x^3-6x^2+11x-6", "answer": "(x-1)(x-2)(x-3)"},
                        {"type": "mcq", "question": "Find f(2) if f(x)=3x^2-2x+1", "options": ["9", "7", "5"],
                         "answer": "9"},
                        {"type": "text", "question": "Solve x^3-3x^2-4x+12=0", "answer": "2,-1,3"},
                        {"type": "mcq", "question": "End behavior of f(x)=x^4-2x^3", "options": ["f→∞", "f→-∞", "f→0"],
                         "answer": "f→∞"},
                        {"type": "text", "question": "Find f'(x) for f(x)=x^3-3x^2", "answer": "3x^2-6x"},
                        {"type": "mcq", "question": "Simplify: (x^3+27)/(x+3)",
                         "options": ["x^2-3x+9", "x^2+3x+9", "x^2-3x-9"], "answer": "x^2-3x+9"},
                        {"type": "text", "question": "Solve x^2+5x+6=0", "answer": "-2,-3"},
                        {"type": "mcq", "question": "Find vertical asymptote of f(x)=1/(x+4)",
                         "options": ["x=-4", "x=4", "x=0"], "answer": "x=-4"},
                        {"type": "text", "question": "Determine the zeros of f(x)=x^2-6x+8", "answer": "2,4"},
                        {"type": "mcq", "question": "Find f(-2) if f(x)=x^2+3x+2", "options": ["0", "-2", "6"],
                         "answer": "0"},
                        {"type": "text", "question": "Vertex of f(x)=x^2-2x-3", "answer": "(1,-4)"}
                    ],
                    "Hard": [
                        {"type": "text", "question": "Find all solutions of 2x^3-3x^2-11x+6=0", "answer": "-1,1,3"},
                        {"type": "mcq", "question": "Simplify (x^3+8)/(x+2)",
                         "options": ["x^2-2x+4", "x^2+2x+4", "x^2-2x-4"], "answer": "x^2-2x+4"},
                        {"type": "text", "question": "Solve for x: x^3-6x^2+11x-6=0", "answer": "1,2,3"},
                        {"type": "mcq", "question": "End behavior of f(x)=-x^3+2x^2", "options": ["f→-∞", "f→∞", "f→0"],
                         "answer": "f→-∞"},
                        {"type": "text", "question": "Find derivative f'(x)=3x^2-12x+5 at x=2", "answer": "-7"},
                        {"type": "mcq", "question": "Simplify: (x^3-27)/(x-3)",
                         "options": ["x^2+3x+9", "x^2-3x+9", "x^2-3x-9"], "answer": "x^2+3x+9"},
                        {"type": "text", "question": "Find all zeros of f(x)=x^4-5x^2+4", "answer": "1,-1,2,-2"},
                        {"type": "mcq", "question": "Identify leading coefficient of f(x)=5x^4-3x^3",
                         "options": ["5", "-3", "3"], "answer": "5"},
                        {"type": "text", "question": "Vertex of f(x)=-2x^2+4x+1", "answer": "(1,3)"},
                        {"type": "mcq", "question": "Horizontal asymptote of f(x)=(3x^2+2)/(x^2+1)",
                         "options": ["y=3", "y=0", "y=2"], "answer": "y=3"},
                        {"type": "text", "question": "Solve x^3-7x^2+10x=0", "answer": "0,2,5"},
                        {"type": "mcq", "question": "End behavior f(x)=2x^4-3x^2", "options": ["f→∞", "f→-∞", "f→0"],
                         "answer": "f→∞"}
                    ]
                },
                "Unit 3": {
                    "Easy": [
                        {"type": "mcq", "question": "Simplify: (x^2-1)/(x-1)", "options": ["x+1","x-1","x^2+1"], "answer": "x+1"},
                        {"type": "text", "question": "Find zeros of f(x)=x^2-9", "answer": "3,-3"},
                        {"type": "mcq", "question": "Evaluate f(1) if f(x)=x^2+3x", "options": ["4","3","2"], "answer": "4"},
                        {"type": "text", "question": "Factor x^2+7x+12", "answer": "(x+3)(x+4)"},
                        {"type": "mcq", "question": "Vertical asymptote of f(x)=1/(x-2)?", "options": ["x=2","x=-2","x=0"], "answer": "x=2"},
                        {"type": "text", "question": "Vertex of f(x)=x^2-6x+5", "answer": "(3,-4)"},
                        {"type": "mcq", "question": "Find f(0) if f(x)=2x^2-4x+1", "options": ["1","0","-1"], "answer": "1"},
                        {"type": "text", "question": "Average rate of change of f(x)=x^2 from x=1 to x=3", "answer": "4"},
                        {"type": "mcq", "question": "Simplify: (x^2-16)/(x-4)", "options": ["x+4","x-4","x^2+4"], "answer": "x+4"},
                        {"type": "text", "question": "Solve x^2-4x+3=0", "answer": "1,3"},
                        {"type": "mcq", "question": "Find f(-1) if f(x)=x^2-2x+1", "options": ["4","2","0"], "answer": "4"},
                        {"type": "text", "question": "Does f(x)=-x^2+2x+1 open up or down?", "answer": "down"}
                    ],
                    "Medium": [
                        {"type": "mcq", "question": "Divide: (x^3-3x^2+2x-4)/(x-1)", "options": ["x^2-2x+4","x^2+2x+4","x^2-2x+2"], "answer": "x^2-2x+4"},
                        {"type": "text", "question": "Factor completely: x^3-6x^2+11x-6", "answer": "(x-1)(x-2)(x-3)"},
                        {"type": "mcq", "question": "Find f(2) if f(x)=x^3-3x^2", "options": ["2","0","4"], "answer": "2"},
                        {"type": "text", "question": "Solve x^3-3x^2-4x+12=0", "answer": "2,-1,3"},
                        {"type": "mcq", "question": "End behavior of f(x)=x^4-2x^2", "options": ["f→∞","f→-∞","f→0"], "answer": "f→∞"},
                        {"type": "text", "question": "Derivative f'(x)=3x^2-6x", "answer": "3x^2-6x"},
                        {"type": "mcq", "question": "Simplify (x^3+27)/(x+3)", "options": ["x^2-3x+9","x^2+3x+9","x^2-3x-9"], "answer": "x^2-3x+9"},
                        {"type": "text", "question": "Solve x^2+5x+6=0", "answer": "-2,-3"},
                        {"type": "mcq", "question": "Vertical asymptote f(x)=1/(x+3)?", "options": ["x=-3","x=3","x=0"], "answer": "x=-3"},
                        {"type": "text", "question": "Zeros of f(x)=x^2-5x+6", "answer": "2,3"},
                        {"type": "mcq", "question": "f(-2) if f(x)=x^2+3x+2", "options": ["0","-2","6"], "answer": "0"},
                        {"type": "text", "question": "Vertex f(x)=x^2-4x+3", "answer": "(2,-1)"}
                    ],
                    "Hard": [
                        {"type": "text", "question": "Solve 2x^3-3x^2-11x+6=0", "answer": "-1,1,3"},
                        {"type": "mcq", "question": "Simplify (x^3+8)/(x+2)", "options": ["x^2-2x+4","x^2+2x+4","x^2-2x-4"], "answer": "x^2-2x+4"},
                        {"type": "text", "question": "Solve x^3-6x^2+11x-6=0", "answer": "1,2,3"},
                        {"type": "mcq", "question": "End behavior f(x)=-x^3+2x^2", "options": ["f→-∞","f→∞","f→0"], "answer": "f→-∞"},
                        {"type": "text", "question": "Derivative f'(x)=3x^2-12x+5 at x=2", "answer": "-7"},
                        {"type": "mcq", "question": "Simplify: (x^3-27)/(x-3)", "options": ["x^2+3x+9","x^2-3x+9","x^2-3x-9"], "answer": "x^2+3x+9"},
                        {"type": "text", "question": "Zeros of f(x)=x^4-5x^2+4", "answer": "1,-1,2,-2"},
                        {"type": "mcq", "question": "Leading coefficient of f(x)=5x^4-3x^3", "options": ["5","-3","3"], "answer": "5"},
                        {"type": "text", "question": "Vertex f(x)=-2x^2+4x+1", "answer": "(1,3)"},
                        {"type": "mcq", "question": "Horizontal asymptote f(x)=(3x^2+2)/(x^2+1)?", "options": ["y=3","y=0","y=2"], "answer": "y=3"},
                        {"type": "text", "question": "Solve x^3-7x^2+10x=0", "answer": "0,2,5"},
                        {"type": "mcq", "question": "End behavior f(x)=2x^4-3x^2", "options": ["f→∞","f→-∞","f→0"], "answer": "f→∞"}

                    ]
                },
                        "Unit 4": {
                    "Easy": [
                        {"type": "mcq", "question": "Simplify: (x^2 - 16)/(x-4)", "options": ["x+4", "x-4", "x^2+4"], "answer": "x+4"},
                        {"type": "text", "question": "Find the zeros of f(x)=x^2-9", "answer": "3,-3"},
                        {"type": "mcq", "question": "Evaluate f(2) if f(x)=3x+5", "options": ["11","7","9"], "answer": "11"},
                        {"type": "text", "question": "Solve for x: 2x-5=9", "answer": "7"},
                        {"type": "mcq", "question": "Which is a vertical asymptote of f(x)=1/(x+3)?", "options": ["x=-3","x=3","x=0"], "answer": "x=-3"},
                        {"type": "text", "question": "Factor completely: x^2-5x+6", "answer": "(x-2)(x-3)"},
                        {"type": "mcq", "question": "Simplify: (x^2+5x+6)/(x+2)", "options": ["x+3","x+2","x+6"], "answer": "x+3"},
                        {"type": "text", "question": "Find the domain of f(x)=1/(x-7)", "answer": "x!=7"},
                        {"type": "mcq", "question": "Simplify: x^2-6x+9", "options": ["(x-3)^2","(x+3)^2","x(x-6)"], "answer": "(x-3)^2"},
                        {"type": "text", "question": "Solve for x: x^2-4x=0", "answer": "0,4"},
                        {"type": "mcq", "question": "Evaluate: f(0) if f(x)=2x+3", "options": ["3","2","0"], "answer": "3"},
                        {"type": "text", "question": "Determine if f(x)=x^2+2x+1 has a maximum or minimum", "answer": "minimum"}
                    ],
                    "Medium": [
                        {"type": "mcq", "question": "Divide: (x^3+3x^2-4)/(x+4)", "options": ["x^2-x+1","x^2+7x+16","x^2-3x+1"], "answer": "x^2-x+1"},
                        {"type": "text", "question": "Find the average rate of change of f(x)=x^2 from x=1 to x=3", "answer": "4"},
                        {"type": "mcq", "question": "Identify the leading coefficient of f(x)=5x^4-2x^3+7", "options": ["5","-2","7"], "answer": "5"},
                        {"type": "text", "question": "Solve for x: x^2-7x+12=0", "answer": "3,4"},
                        {"type": "mcq", "question": "Simplify: (x^2-1)/(x-1)", "options": ["x+1","x-1","x"], "answer": "x+1"},
                        {"type": "text", "question": "Find f'(x) for f(x)=x^3-3x^2+2x", "answer": "3x^2-6x+2"},
                        {"type": "mcq", "question": "End behavior of f(x)=-x^4+2x^2", "options": ["f→-∞ as x→∞","f→∞ as x→∞","f→0 as x→∞"], "answer": "f→-∞ as x→∞"},
                        {"type": "text", "question": "Factor completely: x^3-6x^2+11x-6", "answer": "(x-1)(x-2)(x-3)"},
                        {"type": "mcq", "question": "Simplify: (x^3+8)/(x+2)", "options": ["x^2-2x+4","x^2+2x+4","x^2+4"], "answer": "x^2+2x+4"},
                        {"type": "text", "question": "Determine the vertex of f(x)=-x^2+4x-3", "answer": "(2,1)"},
                        {"type": "mcq", "question": "Vertical asymptote of f(x)=1/(x-5)", "options": ["x=5","x=-5","x=0"], "answer": "x=5"},
                        {"type": "text", "question": "Solve for x: x^2-5x=0", "answer": "0,5"}
                    ],
                    "Hard": [
                        {"type": "text", "question": "Find all real solutions for x: x^4-5x^2+4=0", "answer": "1,-1,2,-2"},
                        {"type": "mcq", "question": "If f(x)=(x^2-4)/(x^2-9), holes in the graph?", "options": ["None","x=2","x=3"], "answer": "None"},
                        {"type": "text", "question": "Find the derivative of f(x)=2x^3-3x^2+4x-5", "answer": "6x^2-6x+4"},
                        {"type": "mcq", "question": "End behavior of f(x)=-x^3+2x^2", "options": ["As x→∞, f(x)→ -∞","As x→∞, f(x)→ ∞","As x→∞, f(x)→ 0"], "answer": "As x→∞, f(x)→ -∞"},
                        {"type": "text", "question": "Solve for x: (x^2-4)/(x^2-9)>0", "answer": "x<-3 or -3<x<-2 or 2<x<3 or x>3"},
                        {"type": "text", "question": "Find all zeros of f(x)=x^4-6x^2+8", "answer": "±√2, ±2"},
                        {"type": "mcq", "question": "Simplify: (x^3+27)/(x+3)", "options": ["x^2-3x+9","x^2+3x+9","x^2-3x-9"], "answer": "x[i^2-3x+9"},
                        {"type": "text", "question": "Determine the vertex of f(x)=-3x^2+12x-5", "answer": "(2,7)"},
                        {"type": "mcq", "question": "Horizontal asymptote of f(x)=(3x^2+2)/(x^2+1)", "options": ["y=3","y=2","y=1"], "answer": "y=3"},
                        {"type": "text", "question": "Solve: x^3-7x^2+14x-8=0", "answer": "1,2,4"},
                        {"type": "mcq", "question": "Simplify: (x^4-16)/(x^2-4)", "options": ["x^2+4","x^2-4","x+4"], "answer": "x^2+4"},
                        {"type": "text", "question": "Derivative of f(x)=4x^4-8x^2+5", "answer": "16x^3-16x"}
                    ]
                }


            }

        math_level = st.selectbox(
            "Select your Math course:",
            ["Algebra 1", "Geometry", "Algebra 2", "AP Precalculus"]
        )

        if math_level == "AP Precalculus":
            unit = st.selectbox(
                "Select the Unit you want to practice:",
                ["Unit 1", "Unit 2", "Unit 3", "Unit 4"],
                key="unit_select"
            )
            difficulty = st.radio(
                "Select difficulty level:",
                ["Easy", "Medium", "Hard"],
             key="difficulty_radio"
         )

    # Initialize show_questions flag
            if "show_questions" not in st.session_state:
                st.session_state.show_questions = False

    # Button to show questions
            if unit and difficulty:
                if st.button("Show Questions", key="show_questions_button"):
                    st.session_state.show_questions = True

    # Display questions only if flag is True
            if st.session_state.show_questions:
        # Initialize user_answers in session_state
                if "user_answers" not in st.session_state:
                    st.session_state.user_answers = {}

                for i, q in enumerate(questions[unit][difficulty], 1):
                    if q["type"] == "mcq":
                        st.session_state.user_answers[i] = st.radio(
                            f"Q{i}: {q['question']}",
                            q["options"],
                            key=f"q_{unit}_{difficulty}_{i}"
                        )
                    else:
                        st.session_state.user_answers[i] = st.text_input(
                            f"Q{i}: {q['question']}",
                            key=f"q_{unit}_{difficulty}_{i}"
                        )

        # Submit button to grade answers
                if st.button("Submit Answers", key=f"submit_answers_{unit}_{difficulty}"):
                    score = 0
                    for i, q in enumerate(questions[unit][difficulty], 1):
                        ans = str(st.session_state.user_answers.get(i, "")).strip().lower()
                        correct = str(q["answer"]).strip().lower()
                        if ans == correct:
                            score += 1

                    st.session_state.last_score = score
                    st.session_state.last_unit = unit
                    st.session_state.last_difficulty = difficulty

                    st.success(f"You scored {score} out of {len(questions[unit][difficulty])}!")

                    # SAVE quiz result
                    st.session_state.quiz_history.append({
                        "subject": "AP Precalculus",
                        "unit": unit,
                        "difficulty": difficulty,
                        "score": score,
                        "total": len(questions[unit][difficulty])
                    })

# ---------- 3️⃣ Study Recommendations ----------
        if st.button("Show Study Recommendations", key="study_recs_button"):
            st.subheader("📌 Personalized Study Recommendations")

            weak_units = analyze_weak_units()

            if not weak_units:
                st.success("🎉 Great job! No weak units detected.")
            else:
                for subject, units in weak_units.items():
                    st.markdown(f"### {subject}")

                    for unit in units:
                        st.markdown(f"**🔹 {unit}**")
                        st.write(get_study_tips(unit))
# ORGANIZATION HELPER TAB
# =============================
with main_tabs[3]:
    st.subheader("📅 Organization Helper")

    # =============================
    # DATABASE
    # =============================
    conn_tasks = sqlite3.connect("tasks.db", check_same_thread=False)
    c_tasks = conn_tasks.cursor()
    c_tasks.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        name TEXT,
        subject TEXT,
        due_date TEXT,
        priority TEXT,
        completed INTEGER
    )
    """)
    conn_tasks.commit()

    # =============================
    # ADD TASK
    # =============================
    st.markdown("### Add a New Task")
    task_name = st.text_input("Task Name")
    subject = st.selectbox("Subject", ["Math", "Spanish", "Science", "History", "Other"])
    due_date = st.date_input("Due Date")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    if st.button("Add Task"):
        c_tasks.execute("INSERT INTO tasks (name, subject, due_date, priority, completed) VALUES (?, ?, ?, ?, ?)",
                        (task_name, subject, due_date.strftime("%Y-%m-%d"), priority, 0))
        conn_tasks.commit()
        st.success(f"Task '{task_name}' added!")

    # =============================
    # VIEW / UPDATE TASKS
    # =============================
    st.markdown("### Your Tasks")
    c_tasks.execute("SELECT * FROM tasks ORDER BY due_date")
    tasks = c_tasks.fetchall()

    for t in tasks:
        task_id, name, subj, due, prio, comp = t
        status = "✅" if comp else "❌"
        cols = st.columns([1,2,2,2,1,1])
        with cols[0]:
            if st.checkbox("", value=comp, key=f"complete_{task_id}"):
                c_tasks.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
                conn_tasks.commit()
                status = "✅"
            else:
                c_tasks.execute("UPDATE tasks SET completed=0 WHERE id=?", (task_id,))
                conn_tasks.commit()
                status = "❌"
        with cols[1]:
            st.write(f"{name}")
        with cols[2]:
            st.write(f"{subj}")
        with cols[3]:
            st.write(f"{due}")
        with cols[4]:
            st.write(f"{prio}")
        with cols[5]:
            if st.button("Delete", key=f"del_{task_id}"):
                c_tasks.execute("DELETE FROM tasks WHERE id=?", (task_id,))
                conn_tasks.commit()
                st.experimental_rerun()

    # =============================
    # SIMPLE CALENDAR VIEW
    # =============================
    st.markdown("### Calendar View (by Due Date)")
    from datetime import datetime
    import pandas as pd

    df_tasks = pd.DataFrame(tasks, columns=["ID","Name","Subject","Due Date","Priority","Completed"])
    if not df_tasks.empty:
        df_tasks["Due Date"] = pd.to_datetime(df_tasks["Due Date"])
        df_tasks = df_tasks.sort_values("Due Date")
        st.dataframe(df_tasks[["Name","Subject","Due Date","Priority","Completed"]])
    else:
        st.info("No tasks added yet. Add tasks above to see them here.")