import streamlit as st
import sqlite3

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
        st.header("Math Quiz")
        math_level = st.selectbox("Select your Math course:", ["Algebra 1", "Geometry", "Algebra 2", "AP Precalculus"])

        # Algebra 1 Questions
        if math_level == "Algebra 1":
            q1 = st.radio("Solve for x: 2x + 5 = 13", ["x = 3", "x = 4", "x = 5"])
            q2 = st.radio("Simplify: 3(x + 4) - 2", ["3x + 10", "3x + 12", "3x + 2"])
            q3 = st.radio("Factor: x^2 + 7x + 10", ["(x+5)(x+2)", "(x+10)(x+1)", "(x+2)(x+5)"])
            q4 = st.radio("Solve: 5x - 9 = 16", ["x = 5", "x = 4", "x = 3"])

        # Geometry Questions
        elif math_level == "Geometry":
            q1 = st.radio("The sum of angles in a triangle is?", ["180°", "360°", "90°"])
            q2 = st.radio("Find the area of a rectangle: length=5, width=3", ["15", "8", "10"])
            q3 = st.radio("The Pythagorean theorem applies to which type of triangle?",
                          ["Right triangle", "Equilateral triangle", "Isosceles triangle"])
            q4 = st.radio("Find the circumference of a circle with radius 4", ["8π", "16π", "12π"])

        # Algebra 2 Questions
        elif math_level == "Algebra 2":
            q1 = st.radio("Factor: x^2 + 5x + 6", ["(x+2)(x+3)", "(x+1)(x+6)", "(x+3)(x+4)"])
            q2 = st.radio("Solve: 2x - 7 = 5", ["x = 6", "x = 5", "x = 4"])
            q3 = st.radio("Simplify: (x^2y)(3xy^2)", ["3x^3y^3", "3x^2y^2", "3x^3y^2"])
            q4 = st.radio("Solve for y: 3y/4 = 9", ["y = 12", "y = 36", "y = 7"])

        # AP Precalculus (FISD Units 1-4)
        # AP Precalculus (FISD Units 1-4)
        # =============================
        # AP Precalculus Quiz by Difficulty
        # =============================
        with quiz_tabs[1]:
            st.header("AP Precalculus Quiz")
            difficulty = st.radio("Select difficulty level:", ["Easy", "Medium", "Hard"])

            # Easy Questions (10)
            easy_questions = [
                "Solve for x: 2x + 3 = 7",
                "Simplify: 3(x+2) - 4",
                "Find the zeros of f(x)=x^2-5x+6",
                "What is the sum of angles in a triangle?",
                "Factor: x^2 + 4x + 3",
                "Evaluate f(2) if f(x)=x^2",
                "Simplify: (x^2 * x^3)",
                "Solve for y: 3y - 6 = 0",
                "Identify the coefficient of x in 7x-2",
                "Graph y = 2x + 1: What is the y-intercept?"
            ]

            # Medium Questions (10)
            medium_questions = [
                "Find the average rate of change of f(x)=x^2+2x from x=1 to x=4",
                "Solve for x: 2^x = 16",
                "Simplify: (3x^2 - 2x) + (x^2 + 4x)",
                "Determine all real zeros of f(x)=x^3-6x^2+11x-6",
                "Find the vertex of y=x^2-4x+3",
                "Evaluate log10(1000)",
                "Solve: 3x^2 - 12 = 0",
                "Simplify the rational function (x^2-9)/(x-3)",
                "Find the period of y=sin(2x)",
                "Convert polar coordinates (r=5, θ=π/3) to rectangular"
            ]

            # Hard Questions (10)
            hard_questions = [
                "Find the derivative of f(x)=3x^3 - 5x^2 + 2x",
                "Solve sin(2θ) = √3/2 for θ in [0,2π]",
                "Multiply matrix [[2,-1],[3,4]] by vector [1,2]",
                "Parametric: x=t^2-1, y=2t+3. Find dy/dx at t=2",
                "Find all critical points of f(x)=x^3-3x^2+2",
                "Evaluate the integral ∫(2x+1)dx",
                "Simplify: (x^4-16)/(x^2-4)",
                "Determine amplitude, period, phase shift of y=3sin(2x-π/4)",
                "Solve log2(x-3)=4",
                "A rotation matrix [[0,-1],[1,0]] is applied to vector [3,4]. Find the new vector"
            ]

            # Display Questions Based on Difficulty
            if difficulty == "Easy":
                st.subheader("Easy Questions")
                for i, q in enumerate(easy_questions, 1):
                    st.radio(f"Q{i}: {q}", ["Option A", "Option B", "Option C"])
            elif difficulty == "Medium":
                st.subheader("Medium Questions")
                for i, q in enumerate(medium_questions, 1):
                    st.radio(f"Q{i}: {q}", ["Option A", "Option B", "Option C"])
            else:
                st.subheader("Hard Questions")
                for i, q in enumerate(hard_questions, 1):
                    st.radio(f"Q{i}: {q}", ["Option A", "Option B", "Option C"])

            st.success("AP Precalculus quiz loaded! Answers are not yet auto-graded.")