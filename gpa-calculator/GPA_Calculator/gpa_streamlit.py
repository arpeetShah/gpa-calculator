import streamlit as st
import sqlite3
import hashlib
import random

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
body {
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
    s1 REAL,
    s2 REAL,
    q1 REAL,
    q2 REAL,
    q3 REAL,
    q4 REAL,
    taken INTEGER,
    gt_year INTEGER,
    PRIMARY KEY (course, section)
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
    "AP Computer Science Principles": 6.0,
    "Instruments": 5.0
}

# =============================
# TOP LEVEL TABS
# =============================
top_tabs = st.tabs(["📘 GPA", "📝 Quiz & Practice Problems"])

# =============================
# GPA TAB
# =============================
with top_tabs[0]:
    tabs = st.tabs(["🏫 Middle School", "🎓 High School", "📊 GPA & Analytics"])

    # -----------------------------
    # Middle School
    # -----------------------------
    with tabs[0]:
        st.header("Middle School Grades")

        # Dropdown for MS courses
        ms_selected = st.multiselect(
            "Select the Middle School courses you took",
            list(courses.keys())
        )

        for course in ms_selected:
            c.execute("""
            SELECT s1, s2, taken, gt_year FROM grades
            WHERE course=? AND section='MS'
            """, (course,))
            row = c.fetchone() or (90.0, 90.0, 0, None)

            s1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, row[0], key=f"ms_s1_{course}")
            s2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, row[1], key=f"ms_s2_{course}")

            gt_year = None
            if course == "GT / AP World History":
                gt_year = st.selectbox(f"{course} Year", [1, 2], index=0, key=f"ms_gt_year")

            c.execute("""
            INSERT OR REPLACE INTO grades
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (course, "MS", s1, s2, None, None, None, None, 1, gt_year))
        conn.commit()

    # -----------------------------
    # High School
    # -----------------------------
    with tabs[1]:
        st.header("High School Grades")
        quarters = st.slider("Quarters Completed", 1, 4, 2)

        hs_selected = st.multiselect(
            "Select the High School courses you are taking",
            list(courses.keys())
        )

        for course in hs_selected:
            c.execute("""
            SELECT q1,q2,q3,q4,taken,gt_year FROM grades
            WHERE course=? AND section='HS'
            """, (course,))
            row = c.fetchone() or (90.0, 90.0, 90.0, 90.0, 0, None)

            grades_list = []
            for i in range(quarters):
                grades_list.append(
                    st.number_input(f"{course} – Quarter {i+1}", 0.0, 100.0, row[i], key=f"hs_q_{course}_{i}")
                )

            gt_year = None
            if course == "GT / AP World History":
                gt_year = st.selectbox(f"{course} Year", [1, 2], index=0, key=f"hs_gt_year")

            padded = grades_list + [None]*(4 - len(grades_list))
            c.execute("""
            INSERT OR REPLACE INTO grades
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (course, "HS", None, None, *padded, 1, gt_year))
        conn.commit()

    # -----------------------------
    # GPA & Analytics
    # -----------------------------
    with tabs[2]:
        st.header("GPA Results & Analytics")

        if st.button("🎯 Calculate GPA"):
            ms_course_gpas = {}
            hs_course_gpas = {}
            weighted_list = []
            unweighted_list = []

            for course, weight in courses.items():
                # MS GPA
                c.execute("SELECT s1, s2,taken FROM grades WHERE course=? AND section='MS'", (course,))
                row = c.fetchone()
                if row and row[2]:
                    avg = (row[0]+row[1])/2
                    ms_course_gpas[course] = avg

                # HS GPA
                c.execute("SELECT q1,q2,q3,q4,taken FROM grades WHERE course=? AND section='HS'", (course,))
                row = c.fetchone()
                if row and row[4]:
                    valid = [x for x in row[:4] if x is not None]
                    if valid:
                        avg = sum(valid)/len(valid)
                        hs_course_gpas[course] = avg
                        weighted_list.append(weighted_gpa(avg, weight))
                        unweighted_list.append(unweighted_gpa(avg))

            if weighted_list:
                weighted_final = round(sum(weighted_list)/len(weighted_list),2)
                unweighted_final = round(sum(unweighted_list)/len(unweighted_list),2)
                st.success(f"🎓 Weighted GPA: {weighted_final}")
                st.success(f"📘 Unweighted GPA: {unweighted_final}")

                st.subheader("📊 GPA Insight")
                # Top and bottom courses
                if hs_course_gpas:
                    max_course = max(hs_course_gpas, key=hs_course_gpas.get)
                    min_course = min(hs_course_gpas, key=hs_course_gpas.get)
                    st.write(f"✅ Best performing HS course: {max_course} ({hs_course_gpas[max_course]:.2f})")
                    st.write(f"⚠️ Lowest performing HS course: {min_course} ({hs_course_gpas[min_course]:.2f})")

# =============================
# Quiz & Practice Problems
# =============================
with top_tabs[1]:
    st.header("📝 Quiz & Practice Problems")
    subjects = list(courses.keys())
    quiz_subject = st.selectbox("Select a subject for quiz/practice", subjects)

    # Example questions (simple dictionary)
    quiz_questions = {
        "Spanish 1": [("What is 'Hello' in Spanish?", "Hola", ["Hola","Adios","Gracias","Por favor"])],
        "Algebra 1": [("Solve 2x+3=7. x=?", "2", ["1","2","3","4"])],
        "Biology": [("Which organelle is the powerhouse of the cell?", "Mitochondria", ["Mitochondria","Nucleus","Ribosome","Chloroplast"])],
        "AP Precalculus": [("sin(90°) = ?", "1", ["0","0.5","1","2"])],
    }

    questions = quiz_questions.get(quiz_subject, [])
    for idx, (q, ans, opts) in enumerate(questions):
        st.write(f"Q{idx+1}: {q}")
        user_answer = st.radio("Choose an answer", opts, key=f"q{idx}_{quiz_subject}")
        if st.button(f"Submit Answer {idx+1}"):
            if user_answer == ans:
                st.success("Correct!")
            else:
                st.error(f"Wrong. Correct answer: {ans}")