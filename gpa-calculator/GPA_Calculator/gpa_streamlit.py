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

# A little space so the title isn't jammed to the top
st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# Main tabs for the whole app
main_tabs = st.tabs([
    "🏠 Welcome",
    "🎓 GPA",
    "📝 Quiz & Practice",
    "🧠 Daily Dashboard",
    "📅 Organization Helper"
])

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
with main_tabs[0]:
    st.subheader("Welcome to EduSphere!")
    st.write(
        "Hey! I created this app/website for YOU to have a convenient way to track your educational path. "
        "There is no platform (until now) which allows you to get your cumulative GPA, and that was the inspiration for this. "
        "Throughout this app, you can track your GPA, analyze it, and practice quizzes to improve your learning! "
        "Additionally, you do not need to give any personal credentials; you just manually input your grades and no one "
        "(including me) will have access to your personal information and grades."
    )
    st.image(
        "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=800&q=80",
        use_column_width=True
    )

# =============================
# TAB 3: DAILY DASHBOARD (ORGANIZATION HELPER)
# =============================
# TAB 3: DAILY DASHBOARD
with main_tabs[3]:
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
            "https://images.unsplash.com/photo-1519452575417-564c1401ecc0?auto=format&fit=crop&w=700&q=80",
            width=220,
        )
        st.markdown(
            "<p style='font-size: 12px; opacity: 0.8; margin-top: 6px;'>Quiet focus mode 🧑‍💻</p>",
            unsafe_allow_html=True
        )

# =============================
# TAB 4: ORGANIZATION HELPER
# =============================
from datetime import date

with main_tabs[4]:
    st.header("📅 Organization Helper")

    # --- Session state for saved tasks ---
    if "org_tasks" not in st.session_state:
        st.session_state.org_tasks = []   # each task will be a dict

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
# =============================
# GPA TAB
# =============================
with main_tabs[1]:
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
                        key=f"ms_s{i + 1}_{course}"
                    )
                )

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

            # Prepare values for SQLite insert (make exactly 9 values)
            s1 = grades[0]
            s2 = grades[1] if semesters == 2 else None
            extra = [None, None, None, None]  # HS quarters placeholders

            c.execute("""
                INSERT OR REPLACE INTO grades VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                course, "MS", s1, s2, *extra, gt_year
            ))

        conn.commit()

    # =============================
    # HIGH SCHOOL
    # =============================
    with sub_tabs[1]:
        st.header("High School Grades")

        # Ask once for total quarters completed
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
            # Collect quarter grades for each course
            quarters = st.slider(
                f"Quarters Completed – {course}",
                min_value=1,
                max_value=hs_quarters,
                value=hs_quarters,
                key=f"hs_quarters_{course}"
            )

            q_grades = []
            for i in range(quarters):
                q_grades.append(
                    st.number_input(
                        f"{course} – Quarter {i + 1}",
                        min_value=0.0,
                        max_value=100.0,
                        key=f"hs_q{i + 1}_{course}"
                    )
                )

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

            # Insert into SQLite (exactly 9 values)
            c.execute("""
                INSERT OR REPLACE INTO grades VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                course, "HS", None, None, padded[0], padded[1], padded[2], padded[3], gt_year
            ))

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

                    # Convert grade → GPA
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

                # Group quarters into semesters (Q1+Q2, Q3+Q4)
                for sem_index in range(0, len(q_grades), 2):
                    sem_quarters = q_grades[sem_index:sem_index + 2]

                    raw_avg = sum(sem_quarters) / len(sem_quarters)
                    sem_avg = round(raw_avg)  # 🔥 FIX: ROUND TO WHOLE NUMBER FIRST

                    # Determine weight
                    if course == "GT / AP World History":
                        year = st.session_state.get(f"{course}_year", 1)
                        weight = courses[course][year]
                    else:
                        weight = courses.get(course)

                    # Convert semester grade → GPA
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