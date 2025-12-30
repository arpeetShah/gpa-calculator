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
    section TEXT,
    course TEXT,
    s1 REAL,
    s2 REAL,
    q1 REAL,
    q2 REAL,
    q3 REAL,
    q4 REAL,
    gt_year INTEGER,
    PRIMARY KEY (section, course)
)
""")
conn.commit()

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
# HELPERS
# =============================
def weighted_gpa(avg, weight):
    if weight is None:  # GT/AP World
        weight = 5.5
    return max(weight - ((100 - avg) * 0.1), 0)

def unweighted_gpa(avg):
    if avg >= 90: return 4
    if avg >= 80: return 3
    if avg >= 70: return 2
    if avg >= 60: return 1
    return 0

# =============================
# MAIN APP
# =============================
st.title("🎓 EduSphere")
tabs = st.tabs(["🏫 Middle School", "🎓 High School", "📊 GPA & Analytics"])

# -----------------------------
# MIDDLE SCHOOL
# -----------------------------
with tabs[0]:
    st.header("Middle School Grades")

    selected_ms_courses = st.multiselect(
        "Select your Middle School courses",
        list(courses.keys())
    )

    ms_grades = {}
    for course in selected_ms_courses:
        s1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, 90.0, key=f"ms_s1_{course}")
        s2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, 90.0, key=f"ms_s2_{course}")

        gt_year = None
        if course == "GT / AP World History":
            gt_year = st.radio(f"{course} – Year", [1, 2], horizontal=True, key="gt_year")

        ms_grades[course] = {"s1": s1, "s2": s2, "gt_year": gt_year}

        c.execute("""
        INSERT OR REPLACE INTO grades
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            "MS", course, s1, s2, None, None, None, None, gt_year
        ))
    conn.commit()

# -----------------------------
# HIGH SCHOOL
# -----------------------------
with tabs[1]:
    st.header("High School Grades")

    selected_hs_courses = st.multiselect(
        "Select your High School courses",
        list(courses.keys())
    )

    quarters = st.slider("Quarters Completed", 1, 4, 2)
    hs_grades = {}

    for course in selected_hs_courses:
        q_grades = []
        for i in range(quarters):
            q = st.number_input(f"{course} – Quarter {i+1}", 0.0, 100.0, 90.0, key=f"hs_q_{course}_{i}")
            q_grades.append(q)

        gt_year = None
        if course == "GT / AP World History":
            gt_year = st.radio(f"{course} – Year", [1, 2], horizontal=True, key=f"hs_gt_year")

        hs_grades[course] = {"quarters": q_grades, "gt_year": gt_year}

        padded = q_grades + [None]*(4 - len(q_grades))
        c.execute("""
        INSERT OR REPLACE INTO grades
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            "HS", course, None, None, padded[0], padded[1], padded[2], padded[3], gt_year
        ))
    conn.commit()

# -----------------------------
# GPA & ANALYTICS
# -----------------------------
with tabs[2]:
    st.header("GPA Results & Analytics")

    if st.button("🎯 Calculate GPA"):
        ms_course_gpas = {}
        hs_course_gpas = {}

        # Middle School GPA
        for course, data in ms_grades.items():
            avg = (data["s1"] + data["s2"])/2
            weight = courses[course]
            ms_course_gpas[course] = weighted_gpa(avg, weight)

        # High School GPA
        for course, data in hs_grades.items():
            grades = data["quarters"]
            avg = sum(grades)/len(grades)
            weight = courses[course]
            hs_course_gpas[course] = weighted_gpa(avg, weight)

        weighted_final = round((sum(ms_course_gpas.values()) + sum(hs_course_gpas.values())) / (len(ms_course_gpas)+len(hs_course_gpas)), 2)
        unweighted_final = round((sum([unweighted_gpa((data["s1"]+data["s2"])/2) for data in ms_grades.values()]) +
                                  sum([unweighted_gpa(sum(data["quarters"])/len(data["quarters"])) for data in hs_grades.values()])) / (len(ms_grades)+len(hs_grades)), 2)

        st.success(f"🎓 Weighted GPA: {weighted_final}")
        st.success(f"📘 Unweighted GPA: {unweighted_final}")

        st.subheader("📊 GPA by Class")
        st.write("**Middle School:**")
        st.table({course: round(gpa,2) for course,gpa in ms_course_gpas.items()})
        st.write("**High School:**")
        st.table({course: round(gpa,2) for course,gpa in hs_course_gpas.items()})

        st.subheader("📈 Analysis")
        if hs_course_gpas:
            best_course = max(hs_course_gpas, key=hs_course_gpas.get)
            worst_course = min(hs_course_gpas, key=hs_course_gpas.get)
            st.write(f"✅ Class helping the most: {best_course}")
            st.write(f"⚠️ Class bringing you