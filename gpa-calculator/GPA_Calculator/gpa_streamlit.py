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
            # FULL QUESTION BANK
            # =============================
            questions = {
                "Unit 1": {
                    "Easy": [
                        {"type": "mcq", "question": "Solve for x: x² − 5x + 6 = 0",
                         "options": ["x=2 or 3", "x=1 or 6", "x=0 or 6"], "answer": "x=2 or 3"},
                        {"type": "text", "question": "Find the zeros of f(x) = x² − 4", "answer": "2,-2"},
                        {"type": "mcq", "question": "Simplify: (x² − 9)/(x+3)", "options": ["x−3", "x+3", "x²+3"],
                         "answer": "x−3"},
                        {"type": "text", "question": "Determine if f(x)=−x² + 2x + 3 has a maximum or minimum",
                         "answer": "maximum"},
                        {"type": "mcq", "question": "Find f(2) if f(x)=x²+3x−1", "options": ["9", "7", "5"],
                         "answer": "7"},
                        {"type": "mcq", "question": "Which is a vertical asymptote of f(x)=1/(x−5)?",
                         "options": ["x=5", "x=-5", "x=0"], "answer": "x=5"},
                        {"type": "text", "question": "Find the average rate of change of f(x)=x² from x=1 to x=4",
                         "answer": "7"},
                        {"type": "text", "question": "Factor completely: x³ − 3x² − 4x + 12",
                         "answer": "(x−2)(x−2)(x+3)"},
                        {"type": "mcq", "question": "Identify the leading coefficient of f(x)=3x⁴−2x³+5",
                         "options": ["3", "−2", "5"], "answer": "3"},
                        {"type": "text", "question": "Solve for x: (x²+2x)/(x²−4) > 0",
                         "answer": "x<-2 or x>0 and x!=2"},
                        {"type": "mcq", "question": "Simplify: (x²+5x+6)/(x+2)", "options": ["x+3", "x+2", "x+6"],
                         "answer": "x+3"},
                        {"type": "text", "question": "Find f(0) for f(x)=−x²+4x−3", "answer": "−3"},
                        {"type": "mcq", "question": "Which is the y-intercept of f(x)=2x²−3x+1?",
                         "options": ["1", "−3", "2"], "answer": "1"}
                    ],
                    "Medium": [
                        {"type": "mcq", "question": "Divide: (2x³+3x²−x+5)/(x+2)",
                         "options": ["2x²−x+3", "2x²+7x+15", "2x²−x+1"], "answer": "2x²−x+3"},
                        {"type": "text", "question": "Factor completely: x³ − 3x² − 4x + 12",
                         "answer": "(x−2)(x−2)(x+3)"},
                        {"type": "mcq", "question": "Vertical asymptote of f(x)=1/(x−5)?",
                         "options": ["x=5", "x=-5", "x=0"], "answer": "x=5"},
                        {"type": "text", "question": "Find average rate of change of f(x)=x² from x=1 to x=4",
                         "answer": "7"},
                        {"type": "mcq", "question": "Leading coefficient of f(x)=3x⁴−2x³+5",
                         "options": ["3", "−2", "5"], "answer": "3"},
                        {"type": "text", "question": "Solve: x³−6x²+11x−6=0", "answer": "1,2,3"},
                        {"type": "mcq", "question": "Simplify: (x³−8)/(x−2)", "options": ["x²+2x+4", "x²−2x+4", "x²+4"],
                         "answer": "x²+2x+4"},
                        {"type": "text", "question": "Find f'(x) for f(x)=x³−5x²+6x", "answer": "3x²−10x+6"},
                        {"type": "mcq", "question": "End behavior of f(x)=−2x⁴+3x²",
                         "options": ["f→−∞ as x→∞", "f→∞ as x→∞", "f→0 as x→∞"], "answer": "f→−∞ as x→∞"},
                        {"type": "text", "question": "Solve for x: (x²−1)/(x+1)<0", "answer": "x<-1 or 0<x<1"},
                        {"type": "text", "question": "Evaluate f(1) for f(x)=x³−2x²+3", "answer": "2"},
                        {"type": "mcq", "question": "Simplify: (x²−16)/(x−4)", "options": ["x+4", "x−4", "x²−4"],
                         "answer": "x+4"},
                        {"type": "text", "question": "Factor x²−5x+6", "answer": "(x−2)(x−3)"}
                    ],
                    "Hard": [
                        {"type": "text", "question": "Solve 2x⁴−3x³−11x²+6x+9=0", "answer": "-1,1,3/2,-1/2"},
                        {"type": "mcq", "question": "If f(x)=(x²−4)/(x²−9), holes?", "options": ["None", "x=2", "x=3"],
                         "answer": "None"},
                        {"type": "text", "question": "Rate of change at x=2 for f(x)=x³−2x²+x", "answer": "7"},
                        {"type": "mcq", "question": "End behavior of f(x)=−x³+4x²",
                         "options": ["As x→∞, f→−∞", "As x→∞, f→∞", "As x→∞, f→0"], "answer": "As x→∞, f→−∞"},
                        {"type": "text", "question": "Solve (x²+2x)/(x²−4) > 0", "answer": "x<-2 or x>0 and x!=2"},
                        {"type": "text", "question": "Find zeros of f(x)=x⁴−5x²+4", "answer": "1,-1,2,-2"},
                        {"type": "mcq", "question": "Simplify: (x³+27)/(x+3)",
                         "options": ["x²−3x+9", "x²+3x+9", "x²−3x−9"], "answer": "x²−3x+9"},
                        {"type": "text", "question": "Determine vertex of f(x)=−2x²+4x+1", "answer": "(1,3)"},
                        {"type": "mcq", "question": "Horizontal asymptote of f(x)=(2x²+3)/(x²+1)",
                         "options": ["y=2", "y=0", "y=3"], "answer": "y=2"},
                        {"type": "text", "question": "Solve x³−6x²+11x−6=0", "answer": "1,2,3"},
                        {"type": "text", "question": "Evaluate derivative f'(x)=3x²−2x at x=1", "answer": "1"},
                        {"type": "mcq", "question": "Find domain of f(x)=1/(x−3)", "options": ["x≠3", "x≠0", "x>0"],
                         "answer": "x≠3"},
                        {"type": "text", "question": "Factor x³+8 completely", "answer": "(x+2)(x²−2x+4)"}
                    ]
                },
                # =============================
                # Unit 2
                # =============================
                "Unit 2": {
                    "Easy": [
                        {"type": "mcq", "question": "Simplify: (x+3)(x+2)", "options": ["x²+5x+6", "x²+6x+5", "x²+1"],
                         "answer": "x²+5x+6"},
                        {"type": "text", "question": "Factor x²+5x+6", "answer": "(x+2)(x+3)"},
                        {"type": "mcq", "question": "Solve for x: x²−4x=0",
                         "options": ["x=0 or 4", "x=2 or -2", "x=1 or 4"], "answer": "x=0 or 4"},
                        {"type": "text", "question": "Find zeros of f(x)=x²−9", "answer": "3,-3"},
                        {"type": "mcq", "question": "Which is a horizontal asymptote of f(x)=1/x",
                         "options": ["y=0", "y=1", "y=∞"], "answer": "y=0"},
                        {"type": "text", "question": "Find f(1) if f(x)=2x²+3x−1", "answer": "4"},
                        {"type": "mcq", "question": "Simplify: (x²−1)/(x−1)", "options": ["x+1", "x−1", "x²−1"],
                         "answer": "x+1"},
                        {"type": "text", "question": "Determine if f(x)=x²−4x+3 has a max or min", "answer": "minimum"},
                        {"type": "mcq", "question": "End behavior of f(x)=−x²",
                         "options": ["f→−∞ as x→∞", "f→∞ as x→∞", "f→0 as x→∞"], "answer": "f→−∞ as x→∞"},
                        {"type": "text", "question": "Find derivative f'(x)=3x²−2x at x=1", "answer": "1"},
                        {"type": "mcq", "question": "Simplify: (x²+2x)/(x)", "options": ["x+2", "x−2", "2x"],
                         "answer": "x+2"},
                        {"type": "text", "question": "Factor x³+3x²+2x", "answer": "x(x+1)(x+2)"},
                        {"type": "mcq", "question": "Identify leading coefficient of f(x)=5x³−2x²+1",
                         "options": ["5", "−2", "1"], "answer": "5"}
                    ],
                    "Medium": [
                        # 12–13 medium questions for unit 2
                        {"type": "mcq", "question": "Divide: (x³+2x²−x−2)/(x+2)", "options": ["x²−1", "x²+1", "x²−x"],
                         "answer": "x²−1"},
                        {"type": "text", "question": "Find f'(x) for f(x)=x³−6x²+11x−6", "answer": "3x²−12x+11"},
                        {"type": "mcq", "question": "Simplify: (x³−8)/(x−2)", "options": ["x²+2x+4", "x²−2x+4", "x²+4"],
                         "answer": "x²+2x+4"},
                        {"type": "text", "question": "Find average rate of change of f(x)=x²+2x from 1 to 3",
                         "answer": "6"},
                        {"type": "mcq", "question": "Vertical asymptote of f(x)=1/(x−4)?",
                         "options": ["x=4", "x=0", "x=−4"], "answer": "x=4"},
                        {"type": "text", "question": "Factor x³−3x²−4x+12", "answer": "(x−2)(x−2)(x+3)"},
                        {"type": "mcq", "question": "Find f(2) if f(x)=x²−x−6", "options": ["0", "1", "−2"],
                         "answer": "0"},
                        {"type": "text", "question": "Determine vertex of f(x)=−2x²+4x+1", "answer": "(1,3)"},
                        {"type": "mcq", "question": "End behavior of f(x)=−x³+3x²",
                         "options": ["f→−∞ as x→∞", "f→∞ as x→∞", "f→0 as x→∞"], "answer": "f→−∞ as x→∞"},
                        {"type": "text", "question": "Solve x²−4x+3=0", "answer": "1,3"},
                        {"type": "mcq", "question": "Simplify: (x²+5x+6)/(x+2)", "options": ["x+3", "x+2", "x+6"],
                         "answer": "x+3"},
                        {"type": "text", "question": "Find zeros of f(x)=x³−3x²−4x+12", "answer": "2,−1,3"},
                        {"type": "mcq", "question": "Domain of f(x)=1/(x−2)", "options": ["x≠2", "x≠0", "x>0"],
                         "answer": "x≠2"}
                    ],
                    "Hard": [
                        # 12–13 hard questions for unit 2
                        {"type": "text", "question": "Solve 2x⁴−5x³+3x²−x+2=0", "answer": "..."},
                        {"type": "mcq", "question": "End behavior of f(x)=−2x³+5x²", "options": ["f→−∞", "f→∞", "f→0"],
                         "answer": "f→−∞"},
                        {"type": "text", "question": "Find derivative f'(x)=3x²−2x+1 at x=2", "answer": "9"},
                        {"type": "mcq", "question": "Simplify: (x³+27)/(x+3)",
                         "options": ["x²−3x+9", "x²+3x+9", "x²−3x−9"], "answer": "x²−3x+9"},
                        {"type": "text", "question": "Find all zeros of f(x)=x⁴−5x²+4", "answer": "1,−1,2,−2"},
                        {"type": "mcq", "question": "Horizontal asymptote of f(x)=(3x²+2)/(x²+1)",
                         "options": ["y=3", "y=0", "y=2"], "answer": "y=3"},
                        {"type": "text", "question": "Factor x³+8 completely", "answer": "(x+2)(x²−2x+4)"},
                        {"type": "mcq", "question": "Domain of f(x)=1/(x²−4)", "options": ["x≠2,x≠−2", "x>0", "x≠0"],
                         "answer": "x≠2,x≠−2"},
                        {"type": "text", "question": "Solve x³−6x²+11x−6=0", "answer": "1,2,3"},
                        {"type": "mcq", "question": "Leading coefficient of f(x)=4x⁴−2x³+1",
                         "options": ["4", "−2", "1"], "answer": "4"},
                        {"type": "text", "question": "Find f'(x) for f(x)=x³−x²+2x−1", "answer": "3x²−2x+2"},
                        {"type": "mcq", "question": "Simplify: (x³−1)/(x−1)", "options": ["x²+x+1", "x²−x+1", "x²+1"],
                         "answer": "x²+x+1"},
                        {"type": "text", "question": "Determine vertex of f(x)=−3x²+6x−1", "answer": "(1,2)"}
                    ]
                },
                # Units 3 and 4 can be filled similarly in the same format
                "Unit 3": {"Easy": [], "Medium": [], "Hard": []},
                "Unit 4": {"Easy": [], "Medium": [], "Hard": []}
            }

            # =============================
            # DISPLAY QUESTIONS
            # =============================
            if st.session_state.show_questions:
                if unit in questions and difficulty in questions[unit]:
                    selected_questions = questions[unit][difficulty]

                    st.subheader(f"{unit} — {difficulty} Questions")
                    user_answers = {}
                    for i, q in enumerate(selected_questions, 1):
                        if q["type"] == "mcq":
                            user_answers[i] = st.radio(f"Q{i}: {q['question']}", q["options"], key=f"precalc_q_{i}")
                        else:
                            user_answers[i] = st.text_input(f"Q{i}: {q['question']}", key=f"precalc_q_{i}")

                    if st.button("Submit Answers"):
                        score = 0
                        for i, q in enumerate(selected_questions, 1):
                            if str(user_answers[i]).strip().lower() == str(q["answer"]).strip().lower():
                                score += 1
                        st.success(f"🎯 You scored {score} / {len(selected_questions)}")
                else:
                    st.warning("No questions available for this unit and difficulty.")