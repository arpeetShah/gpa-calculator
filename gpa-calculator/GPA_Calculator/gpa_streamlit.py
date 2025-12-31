import streamlit as st
import sqlite3

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
    "GT / AP World History": None,
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

main_tabs = st.tabs(["🏠 Welcome", "🎓 GPA", "📝 Quiz & Practice"])

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
    st.subheader("GPA Tracker")

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
                gt_year = st.text_input(f"Year for {course}", key="ms_gt_year")

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
                gt_year = st.text_input(f"Year for {course}", key="hs_gt_year")

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

            # MS GPA
            for course, (s1, s2) in ms_course_grades.items():
                avg = (s1 + s2)/2
                weight = courses[course] if courses[course] is not None else 5.0
                weighted.append(weighted_gpa(avg, weight))
                unweighted.append(unweighted_gpa(avg))

            # HS GPA
            for course, grades in hs_course_grades.items():
                avg = sum(grades)/len(grades)
                weight = courses[course] if courses[course] is not None else 5.0
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

        math_level = st.selectbox(
            "Select your Math course:",
            ["Algebra 1", "Geometry", "Algebra 2", "AP Precalculus"]
        )

        if math_level == "AP Precalculus":

            unit = st.selectbox(
                "Select the Unit you want to practice:",
                ["Unit 1", "Unit 2", "Unit 3", "Unit 4"]
            )

            difficulty = st.radio(
                "Select difficulty level:",
                ["Easy", "Medium", "Hard"]
            )

            if "show_questions" not in st.session_state:
                st.session_state.show_questions = False

            if st.button("Show Questions"):
                st.session_state.show_questions = True

            # =============================
            # QUESTION BANK
            # =============================
            questions = {
                "Unit 1": {
                    "Easy": [
                        {"type": "mcq", "question": "Solve for x: x² − 5x + 6 = 0",
                         "options": ["x = 2 or 3", "x = 1 or 6", "x = 0 or 6"],
                         "answer": "x = 2 or 3"},

                        {"type": "text",
                         "question": "Find the zeros of f(x) = x² − 4",
                         "answer": "2,-2"},

                        {"type": "mcq",
                         "question": "Simplify: (x² − 9)/(x + 3)",
                         "options": ["x − 3", "x + 3", "x² + 3"],
                         "answer": "x − 3"},

                        {"type": "text",
                         "question": "Does f(x) = −x² + 2x + 3 have a maximum or minimum?",
                         "answer": "maximum"},

                        {"type": "mcq",
                         "question": "Which is a vertical asymptote of f(x) = 1/(x − 5)?",
                         "options": ["x = 5", "x = −5", "x = 0"],
                         "answer": "x = 5"}
                    ],

                    "Medium": [
                        {"type": "mcq",
                         "question": "Divide: (2x³ + 3x² − x + 5)/(x + 2)",
                         "options": ["2x² − x + 3", "2x² + 7x + 15", "2x² − x + 1"],
                         "answer": "2x² − x + 3"},

                        {"type": "text",
                         "question": "Solve: x³ − 6x² + 11x − 6 = 0",
                         "answer": "1,2,3"},

                        {"type": "mcq",
                         "question": "End behavior of f(x) = −2x⁴ + 3x²",
                         "options": [
                             "f → −∞ as x → ∞",
                             "f → ∞ as x → ∞",
                             "f → 0 as x → ∞"
                         ],
                         "answer": "f → −∞ as x → ∞"}
                    ],

                    "Hard": [
                        {"type": "text",
                         "question": "Find all real solutions of 2x⁴ − 3x³ − 11x² + 6x + 9 = 0",
                         "answer": "-1,1,3/2,-1/2"},

                        {"type": "mcq",
                         "question": "Which is the horizontal asymptote of f(x) = (2x² + 3)/(x² + 1)?",
                         "options": ["y = 2", "y = 0", "y = 3"],
                         "answer": "y = 2"}
                    ]
                },

                # ✅ PLACEHOLDERS (prevents mismatch errors)
                "Unit 2": {"Easy": [], "Medium": [], "Hard": []},
                "Unit 3": {"Easy": [], "Medium": [], "Hard": []},
                "Unit 4": {"Easy": [], "Medium": [], "Hard": []}
            }

            # =============================
            # DISPLAY QUESTIONS
            # =============================
            if st.session_state.show_questions:

                selected_questions = questions[unit][difficulty]

                if not selected_questions:
                    st.info("Questions for this unit are coming soon.")
                else:
                    st.subheader(f"{unit} — {difficulty} Questions")

                    user_answers = {}
                    for i, q in enumerate(selected_questions, 1):
                        if q["type"] == "mcq":
                            user_answers[i] = st.radio(
                                f"Q{i}: {q['question']}",
                                q["options"],
                                key=f"precalc_q_{i}"
                            )
                        else:
                            user_answers[i] = st.text_input(
                                f"Q{i}: {q['question']}",
                                key=f"precalc_q_{i}"
                            )

                    if st.button("Submit Answers"):
                        score = 0
                        for i, q in enumerate(selected_questions, 1):
                            if str(user_answers[i]).strip().lower() == str(q["answer"]).strip().lower():
                                score += 1

                        st.success(f"🎯 You scored {score} / {len(selected_questions)}")