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
    year TEXT,
    PRIMARY KEY (course, section)
)
""")
conn.commit()

# =============================
# COURSES AND WEIGHTAGES
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
    "GT / AP World History": None,  # year will be asked
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
# MAIN TABS
# =============================
tabs = st.tabs(["🏠 Welcome", "🎓 GPA", "📝 Quiz & Practice"])

# =============================
# WELCOME TAB
# =============================
with tabs[0]:
    st.header("Welcome to EduSphere!")
    st.image("https://i.imgur.com/Z7d1XJu.png", use_column_width=True)
    st.write("Track your GPA, get insights, and practice quizzes all in one place.")

# =============================
# GPA TAB
# =============================
with tabs[1]:
    st.subheader("Middle School Grades")
    ms_selected = st.multiselect(
        "Select the courses you took (MS)",
        options=list(courses.keys()),
        default=[],
        key="ms_courses"
    )
    ms_grades = {}
    for course in ms_selected:
        s1 = st.number_input(f"{course} – Semester 1 (MS)", 0.0, 100.0, 90.0, key=f"ms_s1_{course}")
        s2 = st.number_input(f"{course} – Semester 2 (MS)", 0.0, 100.0, 90.0, key=f"ms_s2_{course}")
        if course == "GT / AP World History":
            year = st.selectbox(f"{course} Year (MS)", options=["6th", "7th", "8th"], key=f"ms_year_{course}")
        else:
            year = None
        ms_grades[course] = {"s1": s1, "s2": s2, "year": year}
        # Save to DB
        c.execute("""
            INSERT OR REPLACE INTO grades
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (course, "MS", s1, s2, None, None, None, None, year))
    conn.commit()

    st.subheader("High School Grades")
    hs_selected = st.multiselect(
        "Select the courses you took (HS)",
        options=list(courses.keys()),
        default=[],
        key="hs_courses"
    )
    hs_grades = {}
    quarters = st.slider("Quarters Completed", 1, 4, 2)
    for course in hs_selected:
        q_vals = []
        for i in range(quarters):
            q = st.number_input(f"{course} – Quarter {i+1} (HS)", 0.0, 100.0, 90.0, key=f"hs_q_{course}_{i}")
            q_vals.append(q)
        if course == "GT / AP World History":
            year = st.selectbox(f"{course} Year (HS)", options=["9th", "10th", "11th", "12th"], key=f"hs_year_{course}")
        else:
            year = None
        padded = q_vals + [None]*(4 - len(q_vals))
        hs_grades[course] = {"q": padded, "year": year}
        # Save to DB
        c.execute("""
            INSERT OR REPLACE INTO grades
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (course, "HS", None, None, *padded, year))
    conn.commit()

    st.subheader("GPA & Analytics")
    if st.button("🎯 Calculate GPA"):
        weighted, unweighted = [], []
        ms_course_gpas = {}
        hs_course_gpas = {}

        # MS GPA
        for course, data in ms_grades.items():
            avg = (data["s1"] + data["s2"])/2
            if courses[course] is not None:
                g = weighted_gpa(avg, courses[course])
            else:
                g = avg  # for GT / AP World
            ms_course_gpas[course] = g
            if courses[course] is not None:
                weighted.append(g)
                unweighted.append(unweighted_gpa(avg))

        # HS GPA
        for course, data in hs_grades.items():
            valid = [x for x in data["q"] if x is not None]
            if valid:
                avg = sum(valid)/len(valid)
                if courses[course] is not None:
                    g = weighted_gpa(avg, courses[course])
                else:
                    g = avg
                hs_course_gpas[course] = g
                if courses[course] is not None:
                    weighted.append(g)
                    unweighted.append(unweighted_gpa(avg))

        if weighted:
            w = round(sum(weighted)/len(weighted), 2)
            uw = round(sum(unweighted)/len(unweighted), 2)
            st.success(f"🎓 Weighted GPA: {w}")
            st.success(f"📘 Unweighted GPA: {uw}")
            st.subheader("📊 Course Analysis")
            st.table({**ms_course_gpas, **hs_course_gpas})
            best = max({**ms_course_gpas, **hs_course_gpas}, key=lambda k: {**ms_course_gpas, **hs_course_gpas}[k])
            worst = min({**ms_course_gpas, **hs_course_gpas}, key=lambda k: {**ms_course_gpas, **hs_course_gpas}[k])
            st.write(f"✅ Most Boosting: {best}")
            st.write(f"⚠️ Most Dragging: {worst}")
        else:
            st.warning("No courses selected to calculate GPA.")

# =============================
# QUIZ & PRACTICE TAB
# =============================
with tabs[2]:
    st.header("Coming Soon: Quiz & Practice Problems!")
    st.write("This section will let you practice questions and track your scores.")