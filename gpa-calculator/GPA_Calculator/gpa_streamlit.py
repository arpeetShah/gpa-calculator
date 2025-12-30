import streamlit as st
import sqlite3
import hashlib

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
    username TEXT,
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
    PRIMARY KEY (username, course, section)
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
    "Instruments": 5.0
}

# =============================
# SESSION
# =============================
if "user" not in st.session_state:
    st.session_state.user = "Anonymous"

# =============================
# MAIN APP
# =============================
st.title(f"👋 Welcome, {st.session_state.user}")
tabs = st.tabs(["🏫 Middle School", "🎓 High School", "📊 GPA & Analytics"])

# =============================
# MIDDLE SCHOOL
# =============================
with tabs[0]:
    st.header("Middle School Grades")
    ms_course_gpas = {}

    ms_selected = st.multiselect("Select your Middle School Courses", list(courses.keys()), key="ms_select")
    for course in ms_selected:
        c.execute("""
        SELECT s1, s2 FROM grades
        WHERE username=? AND course=? AND section='MS'
        """, (st.session_state.user, course))
        row = c.fetchone() or (90.0, 90.0)

        s1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, row[0], key=f"ms_s1_{course}")
        s2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, row[1], key=f"ms_s2_{course}")

        avg = (s1 + s2) / 2
        ms_course_gpas[course] = avg

        c.execute("""
        INSERT OR REPLACE INTO grades
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            st.session_state.user, course, "MS",
            s1, s2, None, None, None, None,
            1, None
        ))
    conn.commit()

# =============================
# HIGH SCHOOL
# =============================
with tabs[1]:
    st.header("High School Grades")
    hs_course_gpas = {}
    quarters = st.slider("Quarters Completed", 1, 4, 2)

    hs_selected = st.multiselect("Select your High School Courses", list(courses.keys()), key="hs_select")
    for course in hs_selected:
        c.execute("""
        SELECT q1, q2, q3, q4, gt_year FROM grades
        WHERE username=? AND course=? AND section='HS'
        """, (st.session_state.user, course))
        row = c.fetchone() or (90.0, 90.0, 90.0, 90.0, None)

        grades = []
        for i in range(quarters):
            grades.append(st.number_input(f"{course} – Quarter {i+1}", 0.0, 100.0, row[i], key=f"hs_q_{course}_{i}"))
        avg = sum(grades) / len(grades)
        hs_course_gpas[course] = avg

        gt_year = row[4]
        if course == "GT / AP World History":
            gt_year = st.radio("GT/AP World Year", [1, 2], horizontal=True, key="gt_year")

        padded = grades + [None] * (4 - len(grades))

        c.execute("""
        INSERT OR REPLACE INTO grades
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            st.session_state.user, course, "HS",
            None, None,
            *padded,
            1,
            gt_year
        ))
    conn.commit()

# =============================
# GPA & ANALYTICS
# =============================
with tabs[2]:
    st.header("GPA Results & Analytics")

    if st.button("🎯 Calculate GPA"):
        weighted, unweighted = [], []

        # Middle School GPA
        for avg in ms_course_gpas.values():
            weighted.append(avg)  # weight ignored for MS
            unweighted.append(unweighted_gpa(avg))

        # High School GPA
        for course, avg in hs_course_gpas.items():
            weight = courses[course] if courses[course] is not None else 5.5
            weighted.append(weighted_gpa(avg, weight))
            unweighted.append(unweighted_gpa(avg))

        if not weighted:
            st.warning("No courses selected.")
        else:
            w = round(sum(weighted) / len(weighted), 2)
            uw = round(sum(unweighted) / len(unweighted), 2)

            st.success(f"🎓 **Weighted GPA:** {w}")
            st.success(f"📘 **Unweighted GPA:** {uw}")

            # =============================
            # ANALYTICS
            # =============================
            st.subheader("📊 Class Breakdown")
            st.table({
                "Middle School": ms_course_gpas,
                "High School": hs_course_gpas
            })

            # Biggest impact classes
            if hs_course_gpas:
                best_course = max(hs_course_gpas, key=lambda x: weighted_gpa(hs_course_gpas[x], courses[x] if courses[x] else 5.5))
                worst_course = min(hs_course_gpas, key=lambda x: weighted_gpa(hs_course_gpas[x], courses[x] if courses[x] else 5.5))
                st.write(f"✅ Highest Impact: {best_course}")
                st.write(f"⚠️ Lowest Impact: {worst_course}")