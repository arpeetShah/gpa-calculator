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

        math_level = st.selectbox("Select your Math course:", ["Algebra 1", "Geometry", "Algebra 2", "AP Precalculus"])

        if math_level == "AP Precalculus":
            unit = st.selectbox("Select the Unit you want to practice:", ["Unit 1", "Unit 2", "Unit 3", "Unit 4"])
            difficulty = st.radio("Select difficulty level:", ["Easy", "Medium", "Hard"])

            if "show_questions" not in st.session_state:
                st.session_state.show_questions = False

            if st.button("Show Questions"):
                st.session_state.show_questions = True

            if st.session_state.show_questions:
                # Fully finished question bank
                questions = {
                    "Unit 1": {
                        "Easy": [
                            {"type": "mcq", "question": "Solve for x: x^2 - 5x + 6 = 0",
                             "options": ["x=2 or 3", "x=1 or 6", "x=0 or 6"], "answer": "x=2 or 3"},
                            {"type": "text", "question": "Find the zeros of f(x) = x^2 - 4", "answer": "2,-2"},
                            {"type": "mcq", "question": "Simplify: (x^2 - 9)/(x+3)", "options": ["x-3", "x+3", "x^2+3"],
                             "answer": "x-3"},
                            {"type": "text", "question": "Determine if f(x)= -x^2 + 2x + 3 has a maximum or minimum",
                             "answer": "maximum"},
                            {"type": "mcq", "question": "Find f(2) if f(x)=x^2+3x-1", "options": ["9", "7", "5"],
                             "answer": "7"},
                            {"type": "mcq", "question": "Which is a vertical asymptote of f(x)=1/(x-5)?",
                             "options": ["x=5", "x=-5", "x=0"], "answer": "x=5"},
                            {"type": "text", "question": "Find the average rate of change of f(x)=x^2 from x=1 to x=4",
                             "answer": "7"},
                            {"type": "text", "question": "Factor completely: x^3 - 3x^2 - 4x + 12",
                             "answer": "(x-2)(x-2)(x+3)"},
                            {"type": "mcq", "question": "Identify the leading coefficient of f(x)=3x^4-2x^3+5",
                             "options": ["3", "-2", "5"], "answer": "3"},
                            {"type": "text", "question": "Solve for x: (x^2+2x)/(x^2-4) > 0",
                             "answer": "x<-2 or x>0 and x!=2"},
                            {"type": "mcq", "question": "Simplify: x^2 - 4x + 4",
                             "options": ["(x-2)^2", "x(x-4)", "x^2-2"], "answer": "(x-2)^2"},
                            {"type": "text", "question": "Determine the y-intercept of f(x)=2x^2-3x+5", "answer": "5"}
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
                            {"type": "mcq", "question": "Factor: x^2 + 5x + 6",
                             "options": ["(x+2)(x+3)", "(x+1)(x+6)", "(x+3)(x+3)"], "answer": "(x+2)(x+3)"},
                            {"type": "text", "question": "Find the vertex of f(x)=x^2-4x+7", "answer": "(2,3)"}
                        ],
                        "Hard": [
                            {"type": "text",
                             "question": "Find all real solutions for x: 2x^4 - 3x^3 - 11x^2 + 6x + 9 = 0",
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
                            {"type": "mcq", "question": "Simplify: (x^4 - 16)/(x^2-4)",
                             "options": ["x^2+4", "x+4", "x^2-4"], "answer": "x^2+4"},
                            {"type": "text", "question": "Find f'(x) for f(x)=2x^3-9x^2+12x-4", "answer": "6x^2-18x+12"}
                        ]
                    },
                    "Unit 2": {
                        "Easy": [
                            {"type": "mcq", "question": "Simplify: (x+2)^2",
                             "options": ["x^2+4x+4", "x^2+2", "x^2+2x+2"], "answer": "x^2+4x+4"},
                            {"type": "text", "question": "Solve for x: x^2-9=0", "answer": "3,-3"},
                            {"type": "mcq", "question": "Factor: x^2-5x+6",
                             "options": ["(x-2)(x-3)", "(x+2)(x+3)", "(x-1)(x-6)"], "answer": "(x-2)(x-3)"},
                            {"type": "text", "question": "Find zeros of f(x)=x^2-16", "answer": "4,-4"},
                            {"type": "mcq", "question": "Simplify: (x^2-4)/(x+2)", "options": ["x-2", "x+2", "x^2-2"],
                             "answer": "x-2"},
                            {"type": "text", "question": "Determine y-intercept of f(x)=3x^2-2x+1", "answer": "1"},
                            {"type": "mcq", "question": "Solve for x: x^2+4x+4=0", "options": ["x=-2", "x=2", "x=4"],
                             "answer": "x=-2"},
                            {"type": "text", "question": "Vertex of f(x)=x^2-6x+8", "answer": "(3,-1)"},
                            {"type": "mcq", "question": "Simplify: x^2-6x+9",
                             "options": ["(x-3)^2", "(x+3)^2", "(x-9)^2"], "answer": "(x-3)^2"},
                            {"type": "text", "question": "Solve for x: x^2-1=0", "answer": "1,-1"},
                            {"type": "mcq", "question": "Factor completely: x^2+5x+6",
                             "options": ["(x+2)(x+3)", "(x+1)(x+6)", "(x+3)(x+3)"], "answer": "(x+2)(x+3)"},
                            {"type": "text", "question": "Find x-intercept of f(x)=x^2-3x", "answer": "0,3"}
                        ],
                        "Medium": [
                            {"type": "text", "question": "Factor: x^3+3x^2-4", "answer": "(x+4)(x-1)(x+1)"},
                            {"type": "mcq", "question": "Simplify: (x^3+8)/(x+2)",
                             "options": ["x^2-2x+4", "x^2+2x+4", "x^2+4"], "answer": "x^2+2x+4"},
                            {"type": "text", "question": "Solve: x^3-3x^2-4x+12=0", "answer": "2,-1,3"},
                            {"type": "mcq", "question": "End behavior of f(x)=-x^3+4x^2",
                             "options": ["f→∞", "f→-∞", "f→0"], "answer": "f→-∞"},
                            {"type": "text", "question": "Derivative of f(x)=x^3-3x^2+2x", "answer": "3x^2-6x+2"},
                            {"type": "mcq", "question": "Simplify: x^3-27",
                             "options": ["(x-3)(x^2+3x+9)", "(x+3)(x^2-3x+9)", "x^3-27"], "answer": "(x-3)(x^2+3x+9)"},
                            {"type": "text", "question": "Find zeros of f(x)=x^3-6x^2+11x-6", "answer": "1,2,3"},
                            {"type": "mcq", "question": "Factor: x^3+27",
                             "options": ["(x+3)(x^2-3x+9)", "(x+3)(x^2+3x+9)", "x^3+27"], "answer": "(x+3)(x^2-3x+9)"},
                            {"type": "text", "question": "Solve: x^3-1=0", "answer": "1,-1/2+√3/2 i,-1/2-√3/2 i"},
                            {"type": "mcq", "question": "Simplify: (x^3-1)/(x-1)",
                             "options": ["x^2+x+1", "x^2-x+1", "x^2+1"], "answer": "x^2+x+1"},
                            {"type": "text", "question": "Derivative of f(x)=x^3+3x^2+3x+1", "answer": "3x^2+6x+3"},
                            {"type": "mcq", "question": "Simplify: (x^3+1)/(x+1)",
                             "options": ["x^2-x+1", "x^2+x+1", "x^2+1"], "answer": "x^2-x+1"}
                        ],
                        "Hard": [
                            {"type": "mcq", "question": "End behavior of f(x)=-x^4+3x^2?", "options": ["-∞", "∞", "0"],
                             "answer": "-∞"},
                            {"type": "text", "question": "Find all real solutions: 2x^4-3x^3-11x^2+6x+9=0",
                             "answer": "-1,1,3/2,-1/2"},
                            {"type": "mcq", "question": "Simplify: (x^4-16)/(x^2-4)",
                             "options": ["x^2+4", "x+4", "x^2-4"], "answer": "x^2+4"},
                            {"type": "text", "question": "Derivative of f(x)=2x^3-9x^2+12x-4", "answer": "6x^2-18x+12"},
                            {"type": "mcq", "question": "Horizontal asymptote of f(x)=(2x^2+3)/(x^2+1)?",
                             "options": ["y=2", "y=0", "y=3"], "answer": "y=2"},
                            {"type": "text", "question": "Find f'(x) for f(x)=x^4-4x^3+6x^2-4x+1",
                             "answer": "4x^3-12x^2+12x-4"},
                            {"type": "mcq", "question": "Factor: x^4-1",
                             "options": ["(x^2-1)(x^2+1)", "(x-1)^4", "x^4-1"], "answer": "(x^2-1)(x^2+1)"},
                            {"type": "text", "question": "Solve: x^4-5x^2+4=0", "answer": "1,-1,2,-2"},
                            {"type": "mcq", "question": "Simplify: (x^3+27)/(x+3)",
                             "options": ["x^2-3x+9", "x^2+3x+9", "x^2-3x-9"], "answer": "x^2-3x+9"},
                            {"type": "text", "question": "Determine vertex: f(x)=-2x^2+4x+1", "answer": "(1,3)"},
                            {"type": "mcq", "question": "Solve: (x^2-1)/(x+1)>0",
                             "options": ["x<-1 or 0<x<1", "x>1", "x<0"], "answer": "x<-1 or 0<x<1"},
                            {"type": "text", "question": "Derivative of f(x)=x^4-4x^3+4x^2", "answer": "4x^3-12x^2+8x"}
                        ]
                    },
                    "Unit 3": {
                        "Easy": [
                            {"type": "mcq", "question": "sin(30°)?", "options": ["1/2", "√3/2", "0"], "answer": "1/2"},
                            {"type": "text", "question": "cos(60°)?", "answer": "1/2"},
                            {"type": "mcq", "question": "tan(45°)?", "options": ["1", "0", "√3"], "answer": "1"},
                            {"type": "text", "question": "Find sin(90°)", "answer": "1"},
                            {"type": "mcq", "question": "cos(0°)?", "options": ["1", "0", "-1"], "answer": "1"},
                            {"type": "text", "question": "tan(0°)?", "answer": "0"},
                            {"type": "mcq", "question": "sin(0°)?", "options": ["0", "1", "-1"], "answer": "0"},
                            {"type": "text", "question": "cos(90°)?", "answer": "0"},
                            {"type": "mcq", "question": "tan(90°)?", "options": ["undefined", "0", "1"],
                             "answer": "undefined"},
                            {"type": "text", "question": "Find sin(45°)", "answer": "√2/2"},
                            {"type": "mcq", "question": "Find cos(45°)", "options": ["√2/2", "1/2", "√3/2"],
                             "answer": "√2/2"},
                            {"type": "text", "question": "Find tan(30°)", "answer": "1/√3"}
                        ],
                                            "Medium":[
                        {"type":"text","question":"Find sin(120°)","answer":"√3/2"},
                        {"type":"mcq","question":"cos(135°)?","options":["-√2/2","√2/2","-1/2"],"answer":"-√2/2"},
                        {"type":"text","question":"tan(225°)?","answer":"1"},
                        {"type":"mcq","question":"sin(150°)?","options":["1/2","√3/2","-1/2"],"answer":"1/2"},
                        {"type":"text","question":"Find cos(210°)","answer":"-√3/2"},
                        {"type":"mcq","question":"tan(300°)?","options":["-√3","√3","1"],"answer":"-√3"},
                        {"type":"text","question":"sin(330°)?","answer":"-1/2"},
                        {"type":"mcq","question":"cos(225°)?","options":["-√2/2","√2/2","0"],"answer":"-√2/2"},
                        {"type":"text","question":"tan(135°)?","answer":"-1"},
                        {"type":"mcq","question":"Find sin(210°)?","options":["-1/2","1/2","-√3/2"],"answer":"-1/2"},
                        {"type":"text","question":"cos(300°)?","answer":"1/2"},
                        {"type":"mcq","question":"tan(60°)?","options":["√3","1","0"],"answer":"√3"}
                    ],
                    "Hard":[
                        {"type":"text","question":"Solve sin(x)=1/2 for 0≤x<360°","answer":"30°,150°"},
                        {"type":"mcq","question":"Solve cos(x)= -√3/2 for 0≤x<360°","options":["150°,210°","30°,330°","60°,300°"],"answer":"150°,210°"},
                        {"type":"text","question":"Solve tan(x)=1 for 0≤x<360°","answer":"45°,225°"},
                        {"type":"mcq","question":"Find exact value: sin(5π/6)","options":["1/2","√3/2","-1/2"],"answer":"1/2"},
                        {"type":"text","question":"cos(7π/6)?","answer":"-√3/2"},
                        {"type":"mcq","question":"tan(11π/6)?","options":["-√3/3","√3/3","√3"],"answer":"-√3/3"},
                        {"type":"text","question":"Solve 2sin(x)-1=0 for 0≤x<360°","answer":"30°,150°"},
                        {"type":"mcq","question":"Solve cos(2x)=0 for 0≤x<360°","options":["45°,135°,225°,315°","90°,270°","0°,180°"],"answer":"45°,135°,225°,315°"},
                        {"type":"text","question":"Solve sin(2x)=√3/2 for 0≤x<360°","answer":"30°,60°,210°,240°"},
                        {"type":"mcq","question":"Solve cos(x/2)=√2/2 for 0≤x<360°","options":["90°,270°","45°,315°","60°,300°"],"answer":"90°,270°"},
                        {"type":"text","question":"tan(7π/4)?","answer":"-1"},
                        {"type":"mcq","question":"cos(5π/3)?","options":["1/2","-1/2","-√3/2"],"answer":"1/2"}
                    ]
                },
                "Unit 4": {
                    "Easy":[
                        {"type":"mcq","question":"Simplify: (2x+3)(x-4)","options":["2x^2-5x-12","2x^2-5x+12","2x^2+5x-12"],"answer":"2x^2-5x-12"},
                        {"type":"text","question":"Factor: x^2-10x+25","answer":"(x-5)^2"},
                        {"type":"mcq","question":"Simplify: (x+1)^2","options":["x^2+2x+1","x^2+1","x^2+x+1"],"answer":"x^2+2x+1"},
                        {"type":"text","question":"Solve: x^2-16=0","answer":"4,-4"},
                        {"type":"mcq","question":"Factor: x^2-9","options":["(x-3)(x+3)","x^2-3","x^2+3"],"answer":"(x-3)(x+3)"},
                        {"type":"text","question":"Find the vertex of f(x)=x^2-8x+15","answer":"(4,-1)"},
                        {"type":"mcq","question":"Solve: x^2+6x+9=0","options":["x=-3","x=3","x=6"],"answer":"x=-3"},
                        {"type":"text","question":"Determine y-intercept of f(x)=3x^2-2x+1","answer":"1"},
                        {"type":"mcq","question":"Simplify: x^2-4x+4","options":["(x-2)^2","x^2-2x+2","x^2+2"],"answer":"(x-2)^2"},
                        {"type":"text","question":"Factor completely: x^3+3x^2-4","answer":"(x+4)(x-1)(x+1)"},
                        {"type":"mcq","question":"Simplify: (x^3+8)/(x+2)","options":["x^2-2x+4","x^2+2x+4","x^2+4"],"answer":"x^2+2x+4"},
                        {"type":"text","question":"Derivative of f(x)=x^3-3x^2+2x","answer":"3x^2-6x+2"}
                    ],
                    "Medium":[
                        {"type":"text","question":"Solve x^3-6x^2+11x-6=0","answer":"1,2,3"},
                        {"type":"mcq","question":"Simplify: (x^3-27)/(x-3)","options":["x^2+3x+9","x^2-3x+9","x^2+9"],"answer":"x^2+3x+9"},
                        {"type":"text","question":"Factor completely: x^3+27","answer":"(x+3)(x^2-3x+9)"},
                        {"type":"mcq","question":"Derivative: f(x)=x^3+3x^2+3x+1","options":["3x^2+6x+3","3x^2+3x+3","3x^2+3x+1"],"answer":"3x^2+6x+3"},
                        {"type":"text","question":"End behavior of f(x)=-x^3+2x^2","answer":"-∞"},
                        {"type":"mcq","question":"Horizontal asymptote of f(x)=(2x^2+3)/(x^2+1)?","options":["y=2","y=0","y=3"],"answer":"y=2"},
                        {"type":"text","question":"Solve 2x^4-3x^3-11x^2+6x+9=0","answer":"-1,1,3/2,-1/2"},
                        {"type":"mcq","question":"Simplify: (x^4-16)/(x^2-4)","options":["x^2+4","x+4","x^2-4"],"answer":"x^2+4"},
                        {"type":"text","question":"Derivative: f(x)=2x^3-9x^2+12x-4","answer":"6x^2-18x+12"},
                        {"type":"mcq","question":"Factor: x^4-1","options":["(x^2-1)(x^2+1)","(x-1)^4","x^4-1"],"answer":"(x^2-1)(x^2+1)"},
                        {"type":"text","question":"Solve: x^4-5x^2+4=0","answer":"1,-1,2,-2"},
                        {"type":"mcq","question":"Simplify: (x^3+27)/(x+3)","options":["x^2-3x+9","x^2+3x+9","x^2-3x-9"],"answer":"x^2-3x+9"}
                    ],
                    "Hard":[
                        {"type":"text","question":"Derivative of f(x)=x^4-4x^3+4x^2","answer":"4x^3-12x^2+8x"},
                        {"type":"mcq","question":"End behavior of f(x)=-x^4+3x^2?","options":["-∞","∞","0"],"answer":"-∞"},
                        {"type":"text","question":"Solve: cos(2x)=√2/2 for 0≤x<360°","answer":"22.5°,67.5°,202.5°,247.5°"},
                        {"type":"mcq","question":"Solve sin(2x)=1/2 for 0≤x<360°","options":["15°,75°,195°,255°","30°,150°,210°,330°","45°,135°,225°,315°"],"answer":"15°,75°,195°,255°"},
                        {"type":"text","question":"Solve cos(x/2)=√2/2","answer":"90°,270°"},
                        {"type":"mcq","question":"Solve tan(x)=1","options":["45°,225°","135°,315°","30°,210°"],"answer":"45°,225°"},
                        {"type":"text","question":"Simplify: (x^3-1)/(x-1)","answer":"x^2+x+1"},
                        {"type":"mcq","question":"Solve sin(x)=√3/2","options":["60°,120°","30°,150°","45°,135°"],"answer":"60°,120°"},
                        {"type":"text","question":"Solve cos(x)=-1/2","answer":"120°,240°"},
                        {"type":"mcq","question":"Simplify: (x^3+1)/(x+1)","options":["x^2-x+1","x^2+x+1","x^2+1"],"answer":"x^2-x+1"},
                        {"type":"text","question":"Solve sin(2x)=√3/2","answer":"30°,60°,210°,240°"},
                        {"type":"mcq","question":"cos(5π/3)?","options":["1/2","-1/2","-√3/2"],"answer":"1/2"}
                    ]
                }
            }

            # Display questions for selected unit/difficulty
            if unit in questions and difficulty in questions[unit]:
                st.subheader(f"{unit} Questions ({difficulty} level)")
                user_answers = {}
                for i, q in enumerate(questions[unit][difficulty], 1):
                    if q["type"] == "mcq":
                        user_answers[i] = st.radio(f"Q{i}: {q['question']}", q["options"], key=f"q_{i}")
                    else:
                        user_answers[i] = st.text_input(f"Q{i}: {q['question']}", key=f"q_{i}")

                if st.button("Submit Answers"):
                    score = 0
                    for i, q in enumerate(questions[unit][difficulty], 1):
                        ans = str(user_answers[i]).strip().lower()
                        correct = str(q["answer"]).strip().lower()
                        if ans == correct:
                            score += 1
                    st.success(f"You scored {score} out of {len(questions[unit][difficulty])}!")
            else:
                st.warning("No questions available for this unit and difficulty.")