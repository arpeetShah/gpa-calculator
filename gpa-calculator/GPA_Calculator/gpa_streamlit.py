import streamlit as st
import sqlite3
from datetime import date

st.markdown(
    """
    <style>
    .es-card {
        background: rgba(15, 23, 42, 0.85);
        border-radius: 18px;
        padding: 16px 18px;
        border: 1px solid rgba(148, 163, 184, 0.7);
        box-shadow: 0 14px 30px rgba(0,0,0,0.7);
    }
    .es-card-title {
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .es-card-sub {
        font-size: 12px;
        opacity: 0.85;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


tutor_bar_html = """
<a href="?section=tutoring" style="text-decoration:none;">
    <div style="
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 58px;
        background: linear-gradient(135deg, rgba(30,64,175,0.98), rgba(124,58,237,0.96));
        border-top: 1px solid rgba(191,219,254,0.7);
        box-shadow: 0 -10px 25px rgba(0,0,0,0.75);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        z-index: 999;
        cursor: pointer;
    ">
        <div style="
            width: 30px;
            height: 30px;
            border-radius: 999px;
            background: radial-gradient(circle at top, #fde68a, #f97316);
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:18px;
        ">
            📚
        </div>
        <div style="text-align:center; color:#e5e7eb;">
            <div style="font-size:13px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase;">
                Now Offering 1-on-1 Tutoring
            </div>
            <div style="font-size:11px; opacity:0.9;">
                Tap here to see subjects, grades, and how to get started.
            </div>
        </div>
    </div>
</a>
"""

st.markdown(tutor_bar_html, unsafe_allow_html=True)

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

st.markdown(
    """
    <style>
    .page-wrapper {
        max-width: 1100px;
        margin: 0 auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="page-wrapper">', unsafe_allow_html=True)

# --------------------------------
# Handle navigation via URL param
# --------------------------------
params = st.experimental_get_query_params()

# default section (in case nothing chosen yet)
if "section_choice" not in st.session_state:
    st.session_state.section_choice = "🏠 Home & Intro"

# If the bottom bar was clicked (?section=tutoring), jump to Tutoring
if "section" in params:
    if params["section"][0] == "tutoring":
        st.session_state.section_choice = "🎯 Tutoring"
        # Clear the param so refreshing doesn't keep forcing it
        st.experimental_set_query_params()
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
st.markdown(
    """
    <div style="
        display: flex;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 10px;
    ">
        <div style="
            font-size: 30px;
            font-weight: 700;
        ">
            🎓 EduSphere
        </div>
        <div style="
            font-size: 13px;
            font-weight: 500;
            opacity: 0.85;
        ">
            Organize today. Own tomorrow.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --------- TOP-LEVEL DROPDOWN NAV ---------
section = st.selectbox(
    "Where do you want to go?",
    [
        "🏠 Home & Intro",
        "📚 School Tools",
        "🧠 Daily & Planning",
        "🌱 Personal Growth",
        "🎯 Tutoring",
    ],
    key="section_choice",
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
                    <span><strong>Phone:</strong> 469-XXX-1729</span>
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
    st.subheader("📚 School Tools")

    tools_tabs = st.tabs(["📊 GPA", "📝 Quiz & Practice", "🔗 Resource Hub"])

    # =============================
    # TAB 0: GPA CALCULATOR
    # =============================
    with tools_tabs[0]:
        st.header("📊 GPA Calculator")

        # Top summary card
        st.markdown(
            """
            <div class="es-card" style="margin-bottom: 12px;">
                <div class="es-card-title">How this GPA calculator works</div>
                <p class="es-card-sub">
                    • Middle school: each <b>semester grade</b> becomes one GPA entry.<br>
                    • High school: we average <b>2 quarters = 1 semester</b>, then convert that semester grade to GPA.<br>
                    • Weighted GPA uses your course weight (5.0 / 5.5 / 6.0).<br>
                    • Final GPA is the average of all semester GPAs you entered.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        gpa_tabs = st.tabs(["🏫 Middle School", "🎓 High School", "📈 Results & Analytics"])

        # =============================
        # MIDDLE SCHOOL TAB
        # =============================
        with gpa_tabs[0]:
            st.subheader("🏫 Middle School Grades")

            st.markdown(
                """
                <div class="es-card" style="margin-bottom: 8px;">
                    <div class="es-card-title">Enter your middle school semester grades</div>
                    <p class="es-card-sub">
                        • Most classes have 2 semesters.<br>
                        • <b>Health</b> only has 1 semester.<br>
                        • AP World lets you pick Year 1 or Year 2 weight.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            ms_selected = st.multiselect(
                "Select the courses you took (MS)",
                options=list(courses.keys()),
                key="ms_courses",
            )

            # stored for Results tab
            ms_course_grades = {}

            for course in ms_selected:
                # Determine number of semesters (Health = 1, others = 2)
                semesters = 1 if course == "Health" else 2

                # Collect grades dynamically
                grades = []
                for i in range(semesters):
                    grades.append(
                        st.number_input(
                            f"{course} – Semester {i + 1}",
                            min_value=0.0,
                            max_value=100.0,
                            key=f"ms_s{i + 1}_{course}",
                        )
                    )

                ms_course_grades[course] = tuple(grades)

                # Handle AP World year
                gt_year = None
                if course == "GT / AP World History":
                    gt_year = st.selectbox(
                        f"Select year for {course}:",
                        [1, 2],
                        key=f"{course}_year",
                    )
                    weight = courses[course][gt_year]
                else:
                    weight = courses[course]

                # Prepare values for SQLite insert (exactly 9 values)
                s1 = grades[0]
                s2 = grades[1] if semesters == 2 else None
                extra = [None, None, None, None]  # HS quarter placeholders

                c.execute(
                    """
                    INSERT OR REPLACE INTO grades VALUES (?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        course,
                        "MS",
                        s1,
                        s2,
                        *extra,
                        gt_year,
                    ),
                )

            conn.commit()

        # =============================
        # HIGH SCHOOL TAB
        # =============================
        with gpa_tabs[1]:
            st.subheader("🎓 High School Grades")

            st.markdown(
                """
                <div class="es-card" style="margin-bottom: 8px;">
                    <div class="es-card-title">Enter your high school quarter grades</div>
                    <p class="es-card-sub">
                        • There are 4 quarters in a full year.<br>
                        • We convert them as: Q1 + Q2 = Semester 1, Q3 + Q4 = Semester 2.<br>
                        • If you only have 1–2 quarters so far, we use what's available.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Ask once for total quarters completed this year
            hs_quarters = st.number_input(
                "How many quarters have been completed this year?",
                min_value=1,
                max_value=4,
                value=4,
                step=1,
                key="hs_quarters_overall",
            )

            hs_selected = st.multiselect(
                "Select the courses you took (HS)",
                options=list(courses.keys()),
                key="hs_courses",
            )

            # stored for Results tab
            hs_course_grades = {}

            for course in hs_selected:
                # Collect quarter grades for each course
                quarters = st.slider(
                    f"Quarters Completed – {course}",
                    min_value=1,
                    max_value=hs_quarters,
                    value=hs_quarters,
                    key=f"hs_quarters_{course}",
                )

                q_grades = []
                for i in range(quarters):
                    q_grades.append(
                        st.number_input(
                            f"{course} – Quarter {i + 1}",
                            min_value=0.0,
                            max_value=100.0,
                            key=f"hs_q{i + 1}_{course}",
                        )
                    )

                hs_course_grades[course] = q_grades

                # Handle AP World year
                gt_year = None
                if course == "GT / AP World History":
                    gt_year = st.selectbox(
                        f"Select year for {course}:",
                        [1, 2],
                        key=f"{course}_year",
                    )
                    weight = courses[course][gt_year]
                else:
                    weight = courses[course]

                # Pad to 4 quarters for DB
                padded = q_grades + [None] * (4 - len(q_grades))

                # Insert into SQLite (exactly 9 values)
                c.execute(
                    """
                    INSERT OR REPLACE INTO grades VALUES (?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        course,
                        "HS",
                        None,
                        None,
                        padded[0],
                        padded[1],
                        padded[2],
                        padded[3],
                        gt_year,
                    ),
                )

            conn.commit()

        # =============================
        # RESULTS & ANALYTICS TAB
        # =============================
        with gpa_tabs[2]:
            st.subheader("📈 GPA Results & Analytics")

            st.markdown(
                """
                <div class="es-card" style="margin-bottom: 10px;">
                    <div class="es-card-title">Calculate your current GPA</div>
                    <p class="es-card-sub">
                        This combines every middle school semester and every high school semester
                        (built from your quarter grades) into one overall GPA.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

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
                            weight = courses.get(course, 5.0)

                        # Convert grade → GPA
                        w_gpa = weighted_gpa(grade, weight)
                        uw_gpa = unweighted_gpa(grade)

                        weighted.append(w_gpa)
                        unweighted.append(uw_gpa)

                        breakdown_text.append(
                            f"Middle School | {course} | Semester {sem_index}: "
                            f"Grade {grade} → Weighted GPA {w_gpa:.2f}, Unweighted GPA {uw_gpa:.2f}"
                        )

                # ===========================
                # HIGH SCHOOL GPA
                # ===========================
                for course, q_grades in hs_course_grades.items():
                    # Group quarters into semesters (Q1+Q2, Q3+Q4)
                    for sem_index in range(0, len(q_grades), 2):
                        sem_quarters = q_grades[sem_index : sem_index + 2]

                        if not sem_quarters:
                            continue

                        raw_avg = sum(sem_quarters) / len(sem_quarters)
                        sem_avg = round(raw_avg)  # round to whole number first

                        # Determine weight
                        if course == "GT / AP World History":
                            year = st.session_state.get(f"{course}_year", 1)
                            weight = courses[course][year]
                        else:
                            weight = courses.get(course, 5.0)

                        # Convert semester grade → GPA
                        w_gpa = weighted_gpa(sem_avg, weight)
                        uw_gpa = unweighted_gpa(sem_avg)

                        weighted.append(w_gpa)
                        unweighted.append(uw_gpa)

                        breakdown_text.append(
                            f"High School | {course} | Semester {(sem_index // 2) + 1}: "
                            f"Quarter Grades {sem_quarters} → "
                            f"Avg {raw_avg:.2f} → Rounded {sem_avg} → "
                            f"Weighted GPA {w_gpa:.2f}, Unweighted GPA {uw_gpa:.2f}"
                        )

                # ===========================
                # FINAL GPA
                # ===========================
                if not weighted:
                    st.warning("No courses selected in the MS / HS tabs above.")
                else:
                    final_weighted = round(sum(weighted) / len(weighted), 3)
                    final_unweighted = round(sum(unweighted) / len(unweighted), 3)

                    st.success(f"🎓 Final Weighted GPA: {final_weighted}")
                    st.success(f"📘 Final Unweighted GPA: {final_unweighted}")

                    with st.expander("📖 See full GPA calculation breakdown"):
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

        # ============================
        # TOOL TAB 2: RESOURCE HUB
        # ============================
            with tools_tabs[2]:
                st.subheader("🔗 Resource Hub")

                # Make sure the list exists
                if "resources" not in st.session_state:
                    st.session_state.resources = []

                # Slightly smaller left column so it doesn't dominate
                col_left, col_right = st.columns([1.3, 2.7])

                # ---------- LEFT: Add resource (compact) ----------
                with col_left:
                    st.markdown("**Add a resource**")
                    st.caption("Save links you use a lot (Canvas, Desmos, Quizlet, docs, etc.).")

                    res_title = st.text_input(
                        "Name",
                        placeholder="Ex: Desmos Graphing Calculator",
                        key="res_title",
                    )

                    res_url = st.text_input(
                        "Link",
                        placeholder="Ex: fisd.instructure.com",
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
                            # Force full URL so it opens outside Streamlit
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

                # ---------- RIGHT: 3×3 table of tiles ----------
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
                            filtered = [
                                r for r in st.session_state.resources
                                if r["category"] == selected_cat
                            ]

                        if not filtered:
                            st.caption("No resources in this category yet.")
                        else:
                            # Color themes for tiles (cycled)
                            color_schemes = [
                                {  # blue
                                    "bg": "radial-gradient(circle at top left, rgba(59,130,246,0.35), rgba(30,64,175,0.95))",
                                    "border": "rgba(191,219,254,0.9)",
                                },
                                {  # orange
                                    "bg": "radial-gradient(circle at top left, rgba(249,115,22,0.35), rgba(124,45,18,0.95))",
                                    "border": "rgba(253,186,116,0.9)",
                                },
                                {  # green
                                    "bg": "radial-gradient(circle at top left, rgba(34,197,94,0.35), rgba(5,46,22,0.95))",
                                    "border": "rgba(187,247,208,0.9)",
                                },
                                {  # purple
                                    "bg": "radial-gradient(circle at top left, rgba(168,85,247,0.35), rgba(88,28,135,0.95))",
                                    "border": "rgba(233,213,255,0.9)",
                                },
                                {  # teal
                                    "bg": "radial-gradient(circle at top left, rgba(45,212,191,0.35), rgba(15,118,110,0.95))",
                                    "border": "rgba(153,246,228,0.9)",
                                },
                            ]

                            # Limit to 9 items → 3 rows × 3 columns
                            max_tiles = 9
                            display_list = filtered[:max_tiles]

                            # Row-by-row, 3 columns per row
                            for row_start in range(0, len(display_list), 3):
                                cols = st.columns(3)
                                for i in range(3):
                                    idx = row_start + i
                                    if idx >= len(display_list):
                                        break

                                    r = display_list[idx]
                                    scheme = color_schemes[idx % len(color_schemes)]

                                    tile_html = f"""
            <a href="{r['url']}" target="_blank" style="text-decoration:none;">
                <div style="
                    height:110px;
                    border-radius:18px;
                    padding:10px 14px;
                    background:{scheme['bg']};
                    border:1px solid {scheme['border']};
                    box-shadow:0 14px 30px rgba(15,23,42,0.9);
                    cursor:pointer;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    text-align:center;
                    transition:transform 0.12s ease-out, box-shadow 0.12s ease-out;
                "
                    onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 18px 36px rgba(0,0,0,0.95)';"
                    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 14px 30px rgba(15,23,42,0.9)';"
                >
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
                                    with cols[i]:
                                        st.markdown(tile_html, unsafe_allow_html=True)

                            # If more than 9 in this category, tell the user
                            if len(filtered) > max_tiles:
                                st.caption(f"+ {len(filtered) - max_tiles} more saved resources in this category.")

    # =============================
    # TAB 3: WHAT-IF GPA CALCULATOR
    # =============================
    with tools_tabs[3]:
        st.subheader("❓ What-If GPA Calculator")

        st.markdown(
            "See how your **overall weighted GPA** changes if you add new classes with certain grades."
            "<br><br>"
            "This uses the same 6.0 scale and weight system as your main GPA calculator.",
            unsafe_allow_html=True,
        )

        mode = st.radio(
            "Choose a mode:",
            ["Single new class", "Full new semester"],
            key="whatif_gpa_mode",
        )

        st.markdown("---")

        # -------- Shared inputs --------
        current_gpa = st.number_input(
            "Current weighted GPA (on 6.0 scale)",
            min_value=0.0,
            max_value=6.0,
            value=5.0,
            step=0.01,
            key="whatif_current_gpa",
        )

        completed_semesters = st.number_input(
            "How many semester classes have you already completed in total?",
            min_value=0,
            max_value=200,
            value=10,
            step=1,
            key="whatif_completed_semesters",
        )

        # If they have 0 completed, treat total points as 0
        current_total_points = current_gpa * completed_semesters if completed_semesters > 0 else 0.0

        # ---------- MODE 1: Single new class ----------
        if mode == "Single new class":
            st.markdown("### 🎯 Single Class Simulation")

            course_name = st.selectbox(
                "Pick the class you want to simulate:",
                list(courses.keys()),
                key="whatif_single_course",
            )

            # Handle AP World year (different weights)
            ap_world_year = None
            if course_name == "GT / AP World History":
                ap_world_year = st.selectbox(
                    "Which year of AP World is this?",
                    [1, 2],
                    key="whatif_single_apworld_year",
                )
                course_weight = courses[course_name][ap_world_year]
            else:
                course_weight = courses[course_name]

            predicted_grade = st.number_input(
                "Predicted semester grade for this class (%)",
                min_value=0.0,
                max_value=150.0,
                value=95.0,
                step=0.5,
                key="whatif_single_predicted",
            )

            if st.button("Calculate new GPA (single class)", key="whatif_single_calc"):
                # GPA for this one class on 6.0 scale
                class_gpa = weighted_gpa(predicted_grade, course_weight)
                class_gpa = round(class_gpa, 3)

                new_total_points = current_total_points + class_gpa
                new_total_classes = completed_semesters + 1

                new_cum_gpa = new_total_points / new_total_classes if new_total_classes > 0 else 0.0
                new_cum_gpa = round(new_cum_gpa, 3)

                st.success(
                    f"That **{predicted_grade:.1f}%** in **{course_name}** "
                    f"counts as about **{class_gpa:.3f}** on the 6.0 scale."
                )
                st.info(
                    f"Your overall weighted GPA would change from **{current_gpa:.3f}** "
                    f"to about **{new_cum_gpa:.3f}**."
                )

        # ---------- MODE 2: Full new semester ----------
        else:
            st.markdown("### 📚 Full New Semester Simulation")

            num_classes = st.slider(
                "How many classes are you taking this semester?",
                min_value=1,
                max_value=8,
                value=4,
                step=1,
                key="whatif_sem_num_classes",
            )

            st.caption("Fill in each class below with the class name and the semester grade you think you'll get.")

            # Collect class configs
            class_configs = []

            for i in range(1, num_classes + 1):
                st.markdown(f"**Class {i}**")

                course_name = st.selectbox(
                    f"Class {i} name",
                    list(courses.keys()),
                    key=f"whatif_sem_course_{i}",
                )

                ap_world_year = None
                if course_name == "GT / AP World History":
                    ap_world_year = st.selectbox(
                        f"AP World year for Class {i}",
                        [1, 2],
                        key=f"whatif_sem_apworld_year_{i}",
                    )
                    course_weight = courses[course_name][ap_world_year]
                else:
                    course_weight = courses[course_name]

                predicted_grade = st.number_input(
                    f"Predicted semester grade for Class {i} (%)",
                    min_value=0.0,
                    max_value=150.0,
                    value=93.0,
                    step=0.5,
                    key=f"whatif_sem_grade_{i}",
                )

                class_configs.append(
                    {
                        "name": course_name,
                        "weight": course_weight,
                        "grade": predicted_grade,
                        "ap_year": ap_world_year,
                    }
                )

                st.markdown("---")

            if st.button("Calculate new GPA for this whole semester", key="whatif_sem_calc"):
                new_points = []
                breakdown_lines = []

                for cfg in class_configs:
                    class_gpa = weighted_gpa(cfg["grade"], cfg["weight"])
                    class_gpa = round(class_gpa, 3)
                    new_points.append(class_gpa)

                    breakdown_lines.append(
                        f"{cfg['name']}: {cfg['grade']:.1f}% "
                        f"with weight {cfg['weight']} → {class_gpa:.3f} GPA points"
                    )

                total_new_points = sum(new_points)
                total_classes_added = len(new_points)

                total_points_all = current_total_points + total_new_points
                total_classes_all = completed_semesters + total_classes_added

                new_cum_gpa = total_points_all / total_classes_all if total_classes_all > 0 else 0.0
                new_cum_gpa = round(new_cum_gpa, 3)

                st.success(
                    f"With these predicted grades, this semester would add **{total_new_points:.3f}** "
                    f"GPA points across **{total_classes_added}** classes."
                )
                st.info(
                    f"Your overall weighted GPA would go from **{current_gpa:.3f}** "
                    f"to about **{new_cum_gpa:.3f}**."
                )

                st.markdown("#### Class-by-class breakdown")
                for line in breakdown_lines:
                    st.text(line)
elif section == "🧠 Daily & Planning":
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

elif section == "🎯 Tutoring":
    st.header("🎯 Tutoring with Arpeet")

    # Make sure storage exists
    if "tutoring_requests" not in st.session_state:
        st.session_state.tutoring_requests = []

    tabs = st.tabs(["Overview", "Interest Form", "FAQ"])

    # ---------------- TAB 1: OVERVIEW ----------------
    with tabs[0]:
        col_left, col_right = st.columns([3, 2])

        # LEFT: main info
        with col_left:
            st.subheader("Why I’m offering tutoring")

            st.markdown(
                """
                I’m **Arpeet**, a 9th grader at Emerson High School, and I built EduSphere
                to help students stay organized and understand school better.

                Tutoring with me is:
                - 🧠 **Student-to-student** – I get what assignments and tests actually feel like.
                - 🧮 **Focused on understanding**, not just memorizing steps.
                - 🤝 **Chill and low-pressure** – we work through problems together.
                """
            )

            st.markdown("### 📚 Subjects I can help with")

            st.markdown(
                """
                - **Math:** Algebra 1, Geometry, Algebra 2 basics, AP Precalculus foundations  
                - **Social Studies:** GT / AP World History concepts & writing prep  
                - **Spanish:** Beginner conversation & grammar practice  
                - **Organization:** Planning, prioritizing, and using this app to stay on top of work
                """
            )

            st.markdown("### 👥 Who this is for?")
            st.markdown(
                """
                - Middle schoolers who want a head-start on high school  
                - 9th graders who want help with math, AP World, or staying organized  
                - Anyone who wants another student to explain things in simple language
                """
            )

        # RIGHT: quick “how it works” card
        with col_right:
            st.markdown(
                """
                <div style="
                    background: radial-gradient(circle at top left,
                                rgba(59,130,246,0.35),
                                rgba(15,23,42,0.95));
                    border-radius: 18px;
                    padding: 14px 16px;
                    border: 1px solid rgba(148,163,184,0.7);
                    box-shadow: 0 16px 35px rgba(0,0,0,0.7);
                    font-size: 13px;
                ">
                    <div style="font-size: 15px; font-weight: 700; margin-bottom: 6px;">
                        How a tutoring session works
                    </div>
                    <ol style="padding-left: 18px; margin: 0;">
                        <li>Tell me your subject, class, and what you’re stuck on.</li>
                        <li>We pick problems from your homework or similar practice.</li>
                        <li>I walk you through step-by-step and ask you to explain back.</li>
                        <li>We end with a tiny “exit ticket” so you know what you learned.</li>
                    </ol>
                    <div style="margin-top: 10px; font-size: 11px; opacity: 0.8;">
                        Note: This app doesn’t schedule anything by itself –
                        it just collects your info so you (or a parent) can reach out.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ---------------- TAB 2: INTEREST FORM ----------------
    with tabs[1]:
        st.subheader("📥 Tutoring Interest Form")

        st.markdown(
            "Fill this out if you might want tutoring. This doesn’t book anything – "
            "it just organizes your info so it’s easier to reach out and plan."
        )

        # Basic info
        student_name = st.text_input("Your first name (or initials)", key="tutor_name")
        grade = st.selectbox(
            "Your grade",
            ["6th", "7th", "8th", "9th", "10th", "Other"],
            key="tutor_grade",
        )

        subject = st.selectbox(
            "What do you want help with?",
            [
                "Algebra 1",
                "Geometry",
                "Algebra 2 basics",
                "AP Precalculus basics",
                "GT / AP World History",
                "Spanish",
                "Organization / planning",
                "Other",
            ],
            key="tutor_subject",
        )

        st.markdown("**When are you usually free? (You can pick more than one)**")
        availability = st.multiselect(
            "Days / time windows",
            [
                "Weekdays after school",
                "Weekday evenings",
                "Saturday mornings",
                "Saturday afternoons",
                "Sunday",
            ],
            key="tutor_availability",
        )

        contact_pref = st.selectbox(
            "Who should reach out?",
            [
                "Me (student) will reach out to you",
                "My parent/guardian will contact you",
                "We’ll decide later",
            ],
            key="tutor_contact_pref",
        )

        goals = st.text_area(
            "What are your goals or what are you struggling with?",
            placeholder="Ex: I keep messing up factoring… / I don’t understand DBQ structure…",
            key="tutor_goals",
            height=90,
        )

        if st.button("Save my interest", key="tutor_save_interest"):
            if student_name.strip():
                st.session_state.tutoring_requests.append(
                    {
                        "name": student_name.strip(),
                        "grade": grade,
                        "subject": subject,
                        "availability": availability,
                        "contact_pref": contact_pref,
                        "goals": goals.strip(),
                    }
                )
                st.success(
                    "✅ Saved! You can show this page to your parent/guardian when you reach out."
                )
            else:
                st.warning("Please at least put your name or initials so you remember which one is yours.")

        # Show a mini table of saved entries (only visible on your side)
        if st.session_state.tutoring_requests:
            st.markdown("### 🗂 Saved interest entries (only visible on this device)")
            for i, t in enumerate(st.session_state.tutoring_requests, start=1):
                st.markdown(
                    f"""
                    **#{i} – {t['name']} ({t['grade']})**  
                    • Subject: `{t['subject']}`  
                    • Availability: `{", ".join(t['availability']) if t['availability'] else "Not specified"}`  
                    • Contact: `{t['contact_pref']}`  
                    • Goals: `{t['goals'] or "—"}`
                    """
                )

    # ---------------- TAB 3: FAQ ----------------
    with tabs[2]:
        st.subheader("❓ Tutoring FAQ")

        st.markdown("**Q: Is this through school?**")
        st.markdown(
            "A: No, this is just a personal student-to-student tutoring offer, not an official school program."
        )

        st.markdown("**Q: How do we actually contact you?**")
        st.markdown(
            "A: You can use the contact info on the Home section. It’s best if a parent/guardian reaches out."
        )

        st.markdown("**Q: Do you help with homework or just concepts?**")
        st.markdown(
            "A: Both. We can go over your homework problems *and* practice similar ones so you actually understand it."
        )

        st.markdown("**Q: What grades do you prefer working with?**")
        st.markdown(
            "A: Mostly middle school and early high school (up to 9th/10th grade level)."
        )

st.markdown('</div>', unsafe_allow_html=True)

