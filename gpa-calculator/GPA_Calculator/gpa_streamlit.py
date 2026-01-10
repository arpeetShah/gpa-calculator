import streamlit as st
import sqlite3
from datetime import date

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

if "resources" not in st.session_state:
    st.session_state.resources = []   # each: {"title", "url", "category"}

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
    "AP Chemistry": 6.0,
    "AP Human Geography": 6.0,
    "Sports": 5.0,
    "Health": 5.0,
    "Computer Science": 5.5,
    "AP Computer Science": 6.0,
    "Instruments": 5.0,
    "English 1": 5.5,
    "Surv Bus Mark Fin": 5.0,
    "Engineering": 5.0
}

# =============================
# MAIN APP
# =============================
# =============================
# MAIN TITLE + TABS
# =============================
st.title("🎓 EduSphere")
st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --------- TOP-LEVEL DROPDOWN NAV ---------
section = st.selectbox(
    "Where do you want to go?",
    ["🏠 Home & Intro", "📚 School Tools", "🧠 Focus & Planning", "🌱 Personal Growth"]
)
# =============================
# FLOATING "TODAY'S FOCUS" BOX (top-right on all tabs)
# =============================
p1 = st.session_state.get("dash_task1", "").strip()
p2 = st.session_state.get("dash_task2", "").strip()
p3 = st.session_state.get("dash_task3", "").strip()

items = []
if p1:
    items.append(p1)
if p2:
    items.append(p2)
if p3:
    items.append(p3)

if items:
    items_html = "".join(
        f'<li style="font-weight:600; margin-bottom:2px;">{t}</li>'
        for t in items
    )
else:
    items_html = (
        '<li style="opacity:0.75; font-weight:500;">'
        'Set your top 3 in the Daily Dashboard tab.'
        '</li>'
    )

box_html = f"""
<div style="
    position: fixed;
    top: 80px;
    right: 20px;
    width: 230px;
    background: linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,64,175,0.9));
    border-radius: 16px;
    padding: 10px 12px;
    border: 1px solid rgba(148, 163, 184, 0.6);
    box-shadow: 0 8px 18px rgba(0,0,0,0.35);
    font-size: 12px;
    color: #e5e7eb;
    z-index: 999;
">
    <div style="text-align:center; margin-bottom:6px;">
        <span style="
            display:inline-block;
            padding:4px 10px;
            border-radius:999px;
            background: radial-gradient(circle at top, #f97316, #ec4899);
            color:white;
            font-size:11px;
            font-weight:800;
            letter-spacing:0.12em;
            text-transform:uppercase;
        ">
            Today&apos;s Focus
        </span>
    </div>
    <ul style="margin-top:4px; padding-left:18px; margin-bottom:0;">
        {items_html}
    </ul>
</div>
"""

st.markdown(box_html, unsafe_allow_html=True)

# =============================
# TAB 0: WELCOME
# =============================
if section == "🏠 Home & Intro":
    # ----- WELCOME LAYOUT (3 columns) -----
    col_me, col_app, col_image = st.columns([3, 3, 4])

    # LEFT: About Me
    with col_me:
        st.subheader("👋 About Me")
        st.write(
            "Hi, I'm **Arpeet Shah**.\n"
            "- 9th grade student at **Emerson High School**\n"
            "- I care about staying organized, keeping up with school, and keeping some balance.\n"
            "- I built EduSphere so students (including me) have one place to plan and track school."
        )

        st.markdown("**📇 Contact**")
        st.markdown(
            """
            <div style="margin-top:6px; display:flex; flex-direction:column; gap:6px;">
                <div style="
                    padding:7px 12px;
                    border-radius:999px;
                    background:linear-gradient(135deg,#111827,#1f2937);
                    font-size:13px;
                    color:#f9fafb;
                    border:1px solid rgba(148,163,184,0.9);
                    box-shadow:0 4px 10px rgba(0,0,0,0.55);
                    display:flex;
                    align-items:center;
                    gap:6px;
                ">
                    <span style="font-size:15px;">📱</span>
                    <span><strong>Phone:</strong> 469-996-1729</span>
                </div>
                <div style="
                    padding:7px 12px;
                    border-radius:999px;
                    background:linear-gradient(135deg,#022c22,#064e3b);
                    font-size:13px;
                    color:#f9fafb;
                    border:1px solid rgba(167,243,208,0.9);
                    box-shadow:0 4px 10px rgba(0,0,0,0.55);
                    display:flex;
                    align-items:center;
                    gap:6px;
                ">
                    <span style="font-size:15px;">✉️</span>
                    <span><strong>Email:</strong> arpeet.shah.168@k12.friscoisd.org</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # MIDDLE: About the app
    with col_app:
        st.subheader("🌀 What is EduSphere?")
        st.write(
            "- A calm, all-in-one place for school.\n"
            "- Track your GPA, practice problems, and organize your day.\n"
            "- No logins, no personal data stored — just tools for you."
        )

    # RIGHT: Image
    with col_image:
        st.image(
            "https://images.unsplash.com/photo-1589629828693-5533d7a9d731?auto=format&fit=crop&w=900&q=80",
            width=500,
        )

elif section == "📚 School Tools":
    tools_tabs = st.tabs(["📊 GPA", "📝 Quiz & Practice", "🔗 Resource Hub"])
    # ⬆️ everything under this elif must be indented one level
    # put your GPA + Quiz code in here

    with tools_tabs[0]:
        st.header("📊 GPA Calculator")

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
                # Health = 1 semester, everything else = 2
                semesters = 1 if course == "Health" else 2

                grades = []
                for i in range(semesters):
                    grade = st.number_input(
                        f"{course} – Semester {i + 1}",
                        min_value=0.0,
                        max_value=100.0,
                        key=f"ms_s{i + 1}_{course}"
                    )
                    grades.append(grade)

                ms_course_grades[course] = tuple(grades)

                # Handle AP World year
                gt_year = None
                if course == "GT / AP World History":
                    gt_year = st.selectbox(
                        f"Select year for {course}:",
                        [1, 2],
                        key=f"{course}_year"
                    )
                    weight = courses[course][gt_year]
                else:
                    weight = courses[course]

                # ---- Insert into DB (9 columns total) ----
                s1 = grades[0]
                s2 = grades[1] if semesters == 2 else None
                extra = [None, None, None, None]  # q1–q4 placeholders

                c.execute(
                    """
                    INSERT OR REPLACE INTO grades
                    VALUES (?,?,?,?,?,?,?,?,?)
                    """,
                    (course, "MS", s1, s2, *extra, gt_year)
                )

            conn.commit()

        # =============================
        # HIGH SCHOOL
        # =============================
        with sub_tabs[1]:
            st.header("High School Grades")

            # Ask once for max quarters completed this year
            hs_quarters = st.number_input(
                "Enter how many quarters have been completed this year:",
                min_value=1,
                max_value=4,
                value=4,
                step=1
            )

            hs_selected = st.multiselect(
                "Select the courses you took (HS)",
                options=list(courses.keys()),
                key="hs_courses"
            )

            hs_course_grades = {}

            for course in hs_selected:
                # Per-course quarters (up to hs_quarters)
                quarters = st.slider(
                    f"Quarters Completed – {course}",
                    min_value=1,
                    max_value=hs_quarters,
                    value=hs_quarters,
                    key=f"hs_quarters_{course}"
                )

                q_grades = []
                for i in range(quarters):
                    q_grade = st.number_input(
                        f"{course} – Quarter {i + 1}",
                        min_value=0.0,
                        max_value=100.0,
                        key=f"hs_q{i + 1}_{course}"
                    )
                    q_grades.append(q_grade)

                hs_course_grades[course] = q_grades

                # Handle AP World year
                gt_year = None
                if course == "GT / AP World History":
                    gt_year = st.selectbox(
                        f"Select year for {course}:",
                        [1, 2],
                        key=f"{course}_year"
                    )
                    weight = courses[course][gt_year]
                else:
                    weight = courses[course]

                # Pad to 4 quarters for DB
                padded = q_grades + [None] * (4 - len(q_grades))

                c.execute(
                    """
                    INSERT OR REPLACE INTO grades
                    VALUES (?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        course,
                        "HS",
                        None,  # semester1
                        None,  # semester2
                        padded[0],  # q1
                        padded[1],  # q2
                        padded[2],  # q3
                        padded[3],  # q4
                        gt_year
                    )
                )

            conn.commit()

        # =============================
        # GPA & Analytics
        # =============================
        with sub_tabs[2]:
            st.header("📊 GPA Results & Analytics")

            if st.button("🎯 Calculate GPA"):
                weighted = []
                unweighted = []
                breakdown_text = []

                # ===========================
                # MIDDLE SCHOOL GPA
                # ===========================
                for course, sem_grades in ms_course_grades.items():
                    for sem_index, grade in enumerate(sem_grades, start=1):
                        # Determine weight
                        if course == "GT / AP World History":
                            year = st.session_state.get(f"{course}_year", 1)
                            weight = courses[course][year]
                        else:
                            weight = courses.get(course)

                        w_gpa = weighted_gpa(grade, weight)
                        uw_gpa = unweighted_gpa(grade)

                        weighted.append(w_gpa)
                        unweighted.append(uw_gpa)

                        breakdown_text.append(
                            f"Middle School | {course} | Semester {sem_index}: "
                            f"Grade {grade} → Weighted GPA {w_gpa}, Unweighted GPA {uw_gpa}"
                        )

                # ===========================
                # HIGH SCHOOL GPA
                # ===========================
                for course, q_grades in hs_course_grades.items():
                    # Group quarters into semesters: (Q1+Q2), (Q3+Q4)
                    for sem_index in range(0, len(q_grades), 2):
                        sem_quarters = q_grades[sem_index:sem_index + 2]

                        raw_avg = sum(sem_quarters) / len(sem_quarters)
                        sem_avg = round(raw_avg)  # round quarter average to whole number first

                        # Determine weight
                        if course == "GT / AP World History":
                            year = st.session_state.get(f"{course}_year", 1)
                            weight = courses[course][year]
                        else:
                            weight = courses.get(course)

                        w_gpa = weighted_gpa(sem_avg, weight)
                        uw_gpa = unweighted_gpa(sem_avg)

                        weighted.append(w_gpa)
                        unweighted.append(uw_gpa)

                        breakdown_text.append(
                            f"High School | {course} | Semester {(sem_index // 2) + 1}: "
                            f"Quarter Grades {sem_quarters} → "
                            f"Avg {raw_avg:.2f} → Rounded {sem_avg} → "
                            f"Weighted GPA {w_gpa}, Unweighted GPA {uw_gpa}"
                        )

                # ===========================
                # FINAL GPA
                # ===========================
                if not weighted:
                    st.warning("No courses selected.")
                else:
                    final_weighted = round(sum(weighted) / len(weighted), 4)
                    final_unweighted = round(sum(unweighted) / len(unweighted), 4)

                    st.success(f"🎓 Final Weighted GPA: {final_weighted}")
                    st.success(f"📘 Final Unweighted GPA: {final_unweighted}")

                    st.subheader("📖 GPA Calculation Breakdown")
                    for line in breakdown_text:
                        st.text(line)

    with tools_tabs[1]:
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
                q2 = st.radio("Select the correct verb conjugation: 'Tú (hablar) español.'",
                              ["hablas", "hablo", "habla"])
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
                        {"type": "mcq", "question": "Simplify: (x^2 - 9)/(x+3)", "options": ["x+3", "x-3", "x^2+3"],
                         "answer": "x-3"},
                        {"type": "text", "question": "Determine if f(x)= -x^2 + 2x + 3 has a maximum or minimum",
                         "answer": "maximum"},
                        {"type": "mcq", "question": "Find f(2) if f(x)=x^2+3x-1", "options": ["9", "7", "5"],
                         "answer": "7"},
                        {"type": "mcq", "question": "Which is a vertical asymptote of f(x)=1/(x-5)?",
                         "options": ["x=-5", "x=0", "x=5"], "answer": "x=5"},
                        {"type": "text", "question": "Find the average rate of change of f(x)=x^2 from x=1 to x=4",
                         "answer": "7"},
                        {"type": "text", "question": "Factor completely: x^3 - 3x^2 - 4x + 12",
                         "answer": "(x-2)(x-2)(x+3)"},
                        {"type": "mcq", "question": "Identify the leading coefficient of f(x)=3x^4-2x^3+5",
                         "options": ["-2", "3", "5"], "answer": "3"},
                        {"type": "text", "question": "Solve for x: (x^2+2x)/(x^2-4) > 0",
                         "answer": "x<-2 or x>0 and x!=2"},
                        {"type": "mcq", "question": "What is f(0) for f(x)=2x^2-3x+1?", "options": ["0", "1", "-1"],
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
                        {"type": "mcq", "question": "Simplify: (x^2-1)/(x-1)", "options": ["x+1", "x-1", "x^2+1"],
                         "answer": "x+1"},
                        {"type": "text", "question": "Find zeros of f(x)=x^2-9", "answer": "3,-3"},
                        {"type": "mcq", "question": "Evaluate f(1) if f(x)=x^2+3x", "options": ["4", "3", "2"],
                         "answer": "4"},
                        {"type": "text", "question": "Factor x^2+7x+12", "answer": "(x+3)(x+4)"},
                        {"type": "mcq", "question": "Vertical asymptote of f(x)=1/(x-2)?",
                         "options": ["x=2", "x=-2", "x=0"], "answer": "x=2"},
                        {"type": "text", "question": "Vertex of f(x)=x^2-6x+5", "answer": "(3,-4)"},
                        {"type": "mcq", "question": "Find f(0) if f(x)=2x^2-4x+1", "options": ["1", "0", "-1"],
                         "answer": "1"},
                        {"type": "text", "question": "Average rate of change of f(x)=x^2 from x=1 to x=3",
                         "answer": "4"},
                        {"type": "mcq", "question": "Simplify: (x^2-16)/(x-4)", "options": ["x+4", "x-4", "x^2+4"],
                         "answer": "x+4"},
                        {"type": "text", "question": "Solve x^2-4x+3=0", "answer": "1,3"},
                        {"type": "mcq", "question": "Find f(-1) if f(x)=x^2-2x+1", "options": ["4", "2", "0"],
                         "answer": "4"},
                        {"type": "text", "question": "Does f(x)=-x^2+2x+1 open up or down?", "answer": "down"}
                    ],
                    "Medium": [
                        {"type": "mcq", "question": "Divide: (x^3-3x^2+2x-4)/(x-1)",
                         "options": ["x^2-2x+4", "x^2+2x+4", "x^2-2x+2"], "answer": "x^2-2x+4"},
                        {"type": "text", "question": "Factor completely: x^3-6x^2+11x-6", "answer": "(x-1)(x-2)(x-3)"},
                        {"type": "mcq", "question": "Find f(2) if f(x)=x^3-3x^2", "options": ["2", "0", "4"],
                         "answer": "2"},
                        {"type": "text", "question": "Solve x^3-3x^2-4x+12=0", "answer": "2,-1,3"},
                        {"type": "mcq", "question": "End behavior of f(x)=x^4-2x^2", "options": ["f→∞", "f→-∞", "f→0"],
                         "answer": "f→∞"},
                        {"type": "text", "question": "Derivative f'(x)=3x^2-6x", "answer": "3x^2-6x"},
                        {"type": "mcq", "question": "Simplify (x^3+27)/(x+3)",
                         "options": ["x^2-3x+9", "x^2+3x+9", "x^2-3x-9"], "answer": "x^2-3x+9"},
                        {"type": "text", "question": "Solve x^2+5x+6=0", "answer": "-2,-3"},
                        {"type": "mcq", "question": "Vertical asymptote f(x)=1/(x+3)?",
                         "options": ["x=-3", "x=3", "x=0"], "answer": "x=-3"},
                        {"type": "text", "question": "Zeros of f(x)=x^2-5x+6", "answer": "2,3"},
                        {"type": "mcq", "question": "f(-2) if f(x)=x^2+3x+2", "options": ["0", "-2", "6"],
                         "answer": "0"},
                        {"type": "text", "question": "Vertex f(x)=x^2-4x+3", "answer": "(2,-1)"}
                    ],
                    "Hard": [
                        {"type": "text", "question": "Solve 2x^3-3x^2-11x+6=0", "answer": "-1,1,3"},
                        {"type": "mcq", "question": "Simplify (x^3+8)/(x+2)",
                         "options": ["x^2-2x+4", "x^2+2x+4", "x^2-2x-4"], "answer": "x^2-2x+4"},
                        {"type": "text", "question": "Solve x^3-6x^2+11x-6=0", "answer": "1,2,3"},
                        {"type": "mcq", "question": "End behavior f(x)=-x^3+2x^2", "options": ["f→-∞", "f→∞", "f→0"],
                         "answer": "f→-∞"},
                        {"type": "text", "question": "Derivative f'(x)=3x^2-12x+5 at x=2", "answer": "-7"},
                        {"type": "mcq", "question": "Simplify: (x^3-27)/(x-3)",
                         "options": ["x^2+3x+9", "x^2-3x+9", "x^2-3x-9"], "answer": "x^2+3x+9"},
                        {"type": "text", "question": "Zeros of f(x)=x^4-5x^2+4", "answer": "1,-1,2,-2"},
                        {"type": "mcq", "question": "Leading coefficient of f(x)=5x^4-3x^3",
                         "options": ["5", "-3", "3"], "answer": "5"},
                        {"type": "text", "question": "Vertex f(x)=-2x^2+4x+1", "answer": "(1,3)"},
                        {"type": "mcq", "question": "Horizontal asymptote f(x)=(3x^2+2)/(x^2+1)?",
                         "options": ["y=3", "y=0", "y=2"], "answer": "y=3"},
                        {"type": "text", "question": "Solve x^3-7x^2+10x=0", "answer": "0,2,5"},
                        {"type": "mcq", "question": "End behavior f(x)=2x^4-3x^2", "options": ["f→∞", "f→-∞", "f→0"],
                         "answer": "f→∞"}

                    ]
                },
                "Unit 4": {
                    "Easy": [
                        {"type": "mcq", "question": "Simplify: (x^2 - 16)/(x-4)", "options": ["x+4", "x-4", "x^2+4"],
                         "answer": "x+4"},
                        {"type": "text", "question": "Find the zeros of f(x)=x^2-9", "answer": "3,-3"},
                        {"type": "mcq", "question": "Evaluate f(2) if f(x)=3x+5", "options": ["11", "7", "9"],
                         "answer": "11"},
                        {"type": "text", "question": "Solve for x: 2x-5=9", "answer": "7"},
                        {"type": "mcq", "question": "Which is a vertical asymptote of f(x)=1/(x+3)?",
                         "options": ["x=-3", "x=3", "x=0"], "answer": "x=-3"},
                        {"type": "text", "question": "Factor completely: x^2-5x+6", "answer": "(x-2)(x-3)"},
                        {"type": "mcq", "question": "Simplify: (x^2+5x+6)/(x+2)", "options": ["x+3", "x+2", "x+6"],
                         "answer": "x+3"},
                        {"type": "text", "question": "Find the domain of f(x)=1/(x-7)", "answer": "x!=7"},
                        {"type": "mcq", "question": "Simplify: x^2-6x+9", "options": ["(x-3)^2", "(x+3)^2", "x(x-6)"],
                         "answer": "(x-3)^2"},
                        {"type": "text", "question": "Solve for x: x^2-4x=0", "answer": "0,4"},
                        {"type": "mcq", "question": "Evaluate: f(0) if f(x)=2x+3", "options": ["3", "2", "0"],
                         "answer": "3"},
                        {"type": "text", "question": "Determine if f(x)=x^2+2x+1 has a maximum or minimum",
                         "answer": "minimum"}
                    ],
                    "Medium": [
                        {"type": "mcq", "question": "Divide: (x^3+3x^2-4)/(x+4)",
                         "options": ["x^2-x+1", "x^2+7x+16", "x^2-3x+1"], "answer": "x^2-x+1"},
                        {"type": "text", "question": "Find the average rate of change of f(x)=x^2 from x=1 to x=3",
                         "answer": "4"},
                        {"type": "mcq", "question": "Identify the leading coefficient of f(x)=5x^4-2x^3+7",
                         "options": ["5", "-2", "7"], "answer": "5"},
                        {"type": "text", "question": "Solve for x: x^2-7x+12=0", "answer": "3,4"},
                        {"type": "mcq", "question": "Simplify: (x^2-1)/(x-1)", "options": ["x+1", "x-1", "x"],
                         "answer": "x+1"},
                        {"type": "text", "question": "Find f'(x) for f(x)=x^3-3x^2+2x", "answer": "3x^2-6x+2"},
                        {"type": "mcq", "question": "End behavior of f(x)=-x^4+2x^2",
                         "options": ["f→-∞ as x→∞", "f→∞ as x→∞", "f→0 as x→∞"], "answer": "f→-∞ as x→∞"},
                        {"type": "text", "question": "Factor completely: x^3-6x^2+11x-6", "answer": "(x-1)(x-2)(x-3)"},
                        {"type": "mcq", "question": "Simplify: (x^3+8)/(x+2)",
                         "options": ["x^2-2x+4", "x^2+2x+4", "x^2+4"], "answer": "x^2+2x+4"},
                        {"type": "text", "question": "Determine the vertex of f(x)=-x^2+4x-3", "answer": "(2,1)"},
                        {"type": "mcq", "question": "Vertical asymptote of f(x)=1/(x-5)",
                         "options": ["x=5", "x=-5", "x=0"], "answer": "x=5"},
                        {"type": "text", "question": "Solve for x: x^2-5x=0", "answer": "0,5"}
                    ],
                    "Hard": [
                        {"type": "text", "question": "Find all real solutions for x: x^4-5x^2+4=0",
                         "answer": "1,-1,2,-2"},
                        {"type": "mcq", "question": "If f(x)=(x^2-4)/(x^2-9), holes in the graph?",
                         "options": ["None", "x=2", "x=3"], "answer": "None"},
                        {"type": "text", "question": "Find the derivative of f(x)=2x^3-3x^2+4x-5",
                         "answer": "6x^2-6x+4"},
                        {"type": "mcq", "question": "End behavior of f(x)=-x^3+2x^2",
                         "options": ["As x→∞, f(x)→ -∞", "As x→∞, f(x)→ ∞", "As x→∞, f(x)→ 0"],
                         "answer": "As x→∞, f(x)→ -∞"},
                        {"type": "text", "question": "Solve for x: (x^2-4)/(x^2-9)>0",
                         "answer": "x<-3 or -3<x<-2 or 2<x<3 or x>3"},
                        {"type": "text", "question": "Find all zeros of f(x)=x^4-6x^2+8", "answer": "±√2, ±2"},
                        {"type": "mcq", "question": "Simplify: (x^3+27)/(x+3)",
                         "options": ["x^2-3x+9", "x^2+3x+9", "x^2-3x-9"], "answer": "x[i^2-3x+9"},
                        {"type": "text", "question": "Determine the vertex of f(x)=-3x^2+12x-5", "answer": "(2,7)"},
                        {"type": "mcq", "question": "Horizontal asymptote of f(x)=(3x^2+2)/(x^2+1)",
                         "options": ["y=3", "y=2", "y=1"], "answer": "y=3"},
                        {"type": "text", "question": "Solve: x^3-7x^2+14x-8=0", "answer": "1,2,4"},
                        {"type": "mcq", "question": "Simplify: (x^4-16)/(x^2-4)", "options": ["x^2+4", "x^2-4", "x+4"],
                         "answer": "x^2+4"},
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

    with tools_tabs[2]:
        with tools_tabs[2]:
            st.subheader("🔗 Resource Hub")

            # Make sure the list exists
            if "resources" not in st.session_state:
                st.session_state.resources = []

            # Slightly smaller left column so it doesn't dominate
            col_left, col_right = st.columns([1.4, 2.6])

            # ---------- LEFT: Add resource (compact) ----------
            with col_left:
                st.markdown("**Add a resource**")
                st.caption("Save links to tools you use a lot (Desmos, Quizlet, docs, etc.).")

                res_title = st.text_input(
                    "Name",
                    placeholder="Ex: Desmos Graphing Calculator",
                    key="res_title",
                )

                res_url = st.text_input(
                    "Link",
                    placeholder="Ex: desmos.com/calculator",
                    key="res_url",
                )

                res_category = st.selectbox(
                    "Category",
                    ["Math", "Science", "Spanish", "APs", "Research", "Other"],
                    key="res_category",
                )

                if st.button("Save resource", key="res_save_button"):
                    title = res_title.strip()
                    url = res_url.strip()

                    if title and url:
                        # 🔒 Force full URL so it opens outside Streamlit
                        if not (url.startswith("http://") or url.startswith("https://")):
                            url = "https://" + url

                        st.session_state.resources.append(
                            {
                                "title": title,
                                "url": url,
                                "category": res_category,
                            }
                        )
                        st.success("✅ Resource saved!")
                    else:
                        st.warning("Please enter both a name and a link.")

            # ---------- RIGHT: Gradient tiles grid ----------
            with col_right:
                st.markdown("**Your saved resources**")

                if not st.session_state.resources:
                    st.caption("No resources yet. Add a few on the left!")
                else:
                    # Optional: filter by category
                    categories = ["All"] + sorted(
                        list({r["category"] for r in st.session_state.resources})
                    )
                    selected_cat = st.selectbox(
                        "Filter by category",
                        categories,
                        index=0,
                        key="res_filter_cat",
                    )

                    if selected_cat == "All":
                        filtered = st.session_state.resources
                    else:
                        filtered = [r for r in st.session_state.resources if r["category"] == selected_cat]

                    # Build tiles (≈ 3 per row, responsive)
                    # Build tiles (≈ 3 per row, responsive)
                    tiles_html = """
                    <div style="
                        display:flex;
                        flex-wrap:wrap;
                        gap:12px;
                        justify-content:flex-start;
                    ">
                    """

                    for r in filtered:
                        tiles_html += f"""
                        <a href="{r['url']}" target="_blank"
                           style="
                               text-decoration:none;
                               flex:1 1 calc(33.33% - 12px);
                               min-width:190px;
                               max-width:260px;
                           ">
                            <div style="
                                height:110px;
                                border-radius:18px;
                                padding:10px 14px;
                                background:radial-gradient(circle at top left,
                                            rgba(59,130,246,0.34),
                                            rgba(30,64,175,0.9));
                                border:1px solid rgba(191,219,254,0.85);
                                box-shadow:0 14px 30px rgba(15,23,42,0.9);
                                cursor:pointer;
                                display:flex;
                                align-items:center;
                                justify-content:center;
                                text-align:center;
                            ">
                                <div style="
                                    font-size:15px;
                                    font-weight:700;
                                    letter-spacing:0.04em;
                                    color:#e5e7eb;
                                    text-shadow:0 0 10px rgba(15,23,42,0.9);
                                ">
                                    {r['title']}
                                </div>
                            </div>
                        </a>
                        """

                    tiles_html += "</div>"

                    st.markdown(tiles_html, unsafe_allow_html=True)

elif section == "🧠 Focus & Planning":
    focus_tabs = st.tabs(["🧠 Daily Dashboard", "📅 Organization Helper"])

    with focus_tabs[0]:
        st.header("🧠 Daily Dashboard")

        st.markdown(
            """
            <style>
            .dash-card {
                background: rgba(255, 255, 255, 0.06);
                border-radius: 18px;
                padding: 18px 20px;
                border: 1px solid rgba(255, 255, 255, 0.18);
                backdrop-filter: blur(6px);
            }
            .dash-title-pill {
                display: inline-block;
                padding: 4px 10px;
                border-radius: 999px;
                font-size: 11px;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                background: linear-gradient(135deg, #4f46e5, #9333ea);
                color: white;
                margin-bottom: 8px;
            }
            .dash-subtitle {
                font-size: 18px;
                font-weight: 700;
                margin-bottom: 4px;
            }
            .dash-hint {
                font-size: 12px;
                opacity: 0.8;
                margin-top: 6px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns([3, 2])

        # LEFT: priorities inputs
        with col1:
            st.markdown(
                """
                <div class="dash-card">
                    <div class="dash-title-pill">Today</div>
                    <div class="dash-subtitle">Top 3 Priorities</div>
                    <p style="font-size: 13px; opacity: 0.85; margin-bottom: 6px;">
                        Pick the three things that would make today a win.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            task1 = st.text_input("① Priority 1", key="dash_task1")
            task2 = st.text_input("② Priority 2", key="dash_task2")
            task3 = st.text_input("③ Priority 3", key="dash_task3")

            st.markdown(
                """
                <p class="dash-hint">
                ✅ Tip: If everything is a priority, nothing is. Keep this list short and realistic.
                </p>
                """,
                unsafe_allow_html=True
            )

        # RIGHT: image
        with col2:
            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            st.image(
                "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=80",
                width=500,
            )
            st.markdown(
                "<p style='font-size: 12px; opacity: 0.8; margin-top: 6px;'>Quiet focus mode 🧑‍💻</p>",
                unsafe_allow_html=True
            )

    with focus_tabs[1]:
        st.header("📅 Organization Helper")

        # --- Session state for saved tasks ---
        if "org_tasks" not in st.session_state:
            st.session_state.org_tasks = []  # each task will be a dict

        col_left, col_right = st.columns([2, 3])

        # ---------- LEFT: Add a task ----------
        with col_left:
            st.subheader("➕ Add a task to your planner")

            task_date = st.date_input("📆 Date", value=date.today(), key="org_task_date")

            task_course = st.selectbox(
                "📚 Class / Subject",
                list(courses.keys()) + ["Other"],
                key="org_task_course"
            )

            task_title = st.text_input(
                "✏️ Task / Assignment name",
                key="org_task_title"
            )

            task_type = st.selectbox(
                "Type",
                ["Homework", "Test", "Quiz", "Project", "Reminder"],
                key="org_task_type"
            )

            task_priority = st.selectbox(
                "Priority",
                ["Low", "Medium", "High"],
                key="org_task_priority"
            )

            task_est = st.number_input(
                "Estimated time (minutes)",
                min_value=0,
                max_value=300,
                value=30,
                step=5,
                key="org_task_est"
            )

            if st.button("Add to planner", key="org_add_button"):
                if task_title.strip():
                    st.session_state.org_tasks.append({
                        "date": task_date,
                        "course": task_course,
                        "title": task_title.strip(),
                        "type": task_type,
                        "priority": task_priority,
                        "est": task_est,
                    })
                    st.success("✅ Task added to your planner!")
                else:
                    st.warning("Please enter a task / assignment name before adding.")

        # ---------- RIGHT: View tasks ----------
        with col_right:
            st.subheader("📅 Tasks for a specific day")

            view_date = st.date_input(
                "Show tasks for date:",
                value=date.today(),
                key="org_view_date"
            )

            # Filter tasks for that day
            tasks_for_day = [
                t for t in st.session_state.org_tasks
                if t["date"] == view_date
            ]

            if tasks_for_day:
                for t in tasks_for_day:
                    st.markdown(
                        f"""
                            <div style="
                                padding: 8px 10px;
                                margin-bottom: 6px;
                                border-radius: 10px;
                                background: rgba(15,23,42,0.5);
                                border: 1px solid rgba(148,163,184,0.6);
                            ">
                                <strong>{t['title']}</strong><br>
                                <span style="font-size: 12px; opacity: 0.9;">
                                    {t['course']} • {t['type']} • Priority: {t['priority']} • ~{t['est']} min
                                </span>
                            </div>
                            """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No tasks for this date yet. Add one on the left!")

            st.markdown("---")
            st.subheader("📚 All Planned Tasks")

            if st.session_state.org_tasks:
                # Show all tasks in a simple text list
                for t in st.session_state.org_tasks:
                    st.write(
                        f"- {t['date']} • {t['course']} • {t['title']} "
                        f"({t['type']}, {t['priority']}, ~{t['est']} min)"
                    )
            else:
                st.caption("Your planner is empty. Start by adding a task on the left.")


# TAB 3: DAILY DASHBOARD


# =============================
# TAB 4: ORGANIZATION HELPER
# =============================
# =============================
# GPA TAB
# =============================

# =============================
# QUIZ TAB
# =============================

# =============================
# TAB 5: IDEA VAULT
# =============================
elif section == "🌱 Personal Growth":
    tabs = st.tabs(["💡 Idea Vault"])

    # ------------------ TAB 1: IDEA VAULT ------------------
    with tabs[0]:
        st.subheader("💡 Idea Vault")

        # make sure list exists in session_state
        if "idea_vault" not in st.session_state:
            st.session_state.idea_vault = []

        col_left, col_right = st.columns([3, 2])

        # ---- LEFT: add new idea ----
        with col_left:
            idea_title = st.text_input(
                "Idea title",
                placeholder="Ex: App for tracking volunteering hours",
                key="idea_title"
            )

            idea_desc = st.text_area(
                "Details (optional)",
                placeholder="What is it? Why is it cool? Future you will forget unless you write it 😅",
                key="idea_desc",
                height=90
            )

            idea_tag = st.selectbox(
                "Tag",
                ["School", "Project", "Life", "Random"],
                key="idea_tag"
            )

            idea_importance = st.slider(
                "How exciting / important is this?",
                min_value=1,
                max_value=5,
                value=3,
                key="idea_importance"
            )

            if st.button("Save idea", key="save_idea"):
                if idea_title.strip():
                    st.session_state.idea_vault.append(
                        {
                            "title": idea_title.strip(),
                            "desc": idea_desc.strip(),
                            "tag": idea_tag,
                            "importance": idea_importance,
                        }
                    )
                    st.success("Idea saved to your vault 🔐")
                else:
                    st.warning("Give your idea a short title so future-you knows what it was 🙂")

        # ---- RIGHT: show recent ideas ----
        with col_right:
            st.markdown("### 🗂 Recent Ideas")

            if not st.session_state.idea_vault:
                st.caption("No ideas yet. Whenever you get a random thought, drop it here instead of losing it.")
            else:
                # show last 5 ideas, newest first
                for idea in reversed(st.session_state.idea_vault[-5:]):
                    dots = "•" * idea["importance"]
                    st.markdown(
                        f"""
                        <div style="
                            padding:8px 10px;
                            margin-bottom:6px;
                            border-radius:10px;
                            background:rgba(15,23,42,0.7);
                            border:1px solid rgba(148,163,184,0.8);
                        ">
                            <div style="font-size:13px; font-weight:700;">
                                {idea['title']}
                            </div>
                            <div style="font-size:11px; opacity:0.8; margin:2px 0 4px 0;">
                                Tag: <strong>{idea['tag']}</strong> &nbsp;&nbsp; Priority: <span>{dots}</span>
                            </div>
                            <div style="font-size:12px; opacity:0.9;">
                                {idea['desc'] if idea['desc'] else "<i>No extra details yet.</i>"}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                if len(st.session_state.idea_vault) > 5:
                    st.caption(f"+ {len(st.session_state.idea_vault) - 5} more saved ideas in your vault.")