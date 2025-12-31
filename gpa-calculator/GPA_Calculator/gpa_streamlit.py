import streamlit as st
import sqlite3

# =============================
# SESSION STATE INIT
# =============================
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
    st.write("Track GPA, analyze performance, and practice quizzes to improve learning.")
    st.image(
        "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f",
        use_column_width=True
    )

# =============================
# GPA TAB
# =============================
with main_tabs[1]:
    st.subheader("GPA Tracker")
    sub_tabs = st.tabs(["🏫 Middle School", "🎓 High School", "📊 GPA & Analytics"])

    with sub_tabs[0]:
        st.header("Middle School Grades")
        ms_selected = st.multiselect("Select MS courses", list(courses.keys()))
        ms_course_grades = {}
        for course in ms_selected:
            s1 = st.number_input(f"{course} Semester 1", 0.0, 100.0)
            s2 = st.number_input(f"{course} Semester 2", 0.0, 100.0)
            ms_course_grades[course] = (s1, s2)

    with sub_tabs[1]:
        st.header("High School Grades")
        hs_selected = st.multiselect("Select HS courses", list(courses.keys()))
        hs_course_grades = {}
        for course in hs_selected:
            quarters = st.slider(f"Quarters for {course}", 1, 4, 2)
            grades = [st.number_input(f"Q{i+1}", 0.0, 100.0) for i in range(quarters)]
            hs_course_grades[course] = grades

    with sub_tabs[2]:
        if st.button("🎯 Calculate GPA"):
            weighted, unweighted = [], []
            for c, (s1, s2) in ms_course_grades.items():
                avg = (s1 + s2) / 2
                weighted.append(weighted_gpa(avg, courses[c]))
                unweighted.append(unweighted_gpa(avg))
            for c, g in hs_course_grades.items():
                avg = sum(g) / len(g)
                weighted.append(weighted_gpa(avg, courses[c]))
                unweighted.append(unweighted_gpa(avg))
            if weighted:
                st.success(f"Weighted GPA: {round(sum(weighted)/len(weighted),2)}")
                st.success(f"Unweighted GPA: {round(sum(unweighted)/len(unweighted),2)}")

# =============================
# QUIZ TAB
# =============================
with main_tabs[2]:
    st.subheader("Quiz & Practice Problems")
    quiz_tabs = st.tabs(["Spanish", "Math"])

    # =============================
    # MATH QUIZ (FIXED)
    # =============================
    with quiz_tabs[1]:
        st.header("AP Precalculus Quiz")

        unit = st.selectbox("Select Unit", ["Unit 1"])
        difficulty = st.radio("Difficulty", ["Easy", "Medium", "Hard"])

        questions = {
            "Unit 1": {
                "Easy": [
                    {"type": "mcq", "question": "Solve x²−5x+6=0", "options": ["2 or 3", "1 or 6"], "answer": "2 or 3"},
                    {"type": "text", "question": "Zeros of x²−4", "answer": "2,-2"}
                ],
                "Medium": [
                    {"type": "text", "question": "Factor x³−3x²−4x+12", "answer": "(x-2)(x-2)(x+3)"}
                ],
                "Hard": [
                    {"type": "text", "question": "Solve x³−6x²+11x−6=0", "answer": "1,2,3"}
                ]
            }
        }

        if st.button("Show Questions"):
            st.session_state.show_questions = True
            st.session_state.submitted = False

        if st.session_state.show_questions:
            user_answers = {}
            for i, q in enumerate(questions[unit][difficulty], 1):
                key = f"{unit}_{difficulty}_{i}"
                if q["type"] == "mcq":
                    user_answers[i] = st.radio(f"Q{i}: {q['question']}", q["options"], key=key)
                else:
                    user_answers[i] = st.text_input(f"Q{i}: {q['question']}", key=key)

            if st.button("Submit Answers"):
                score = 0
                for i, q in enumerate(questions[unit][difficulty], 1):
                    if str(st.session_state[f"{unit}_{difficulty}_{i}"]).strip().lower() == str(q["answer"]).lower():
                        score += 1
                st.success(f"✅ Score: {score}/{len(questions[unit][difficulty])}")