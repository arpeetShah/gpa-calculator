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
    username TEXT,
    course TEXT,
    section TEXT,
    s1 REAL,
    s2 REAL,
    q1 REAL,
    q2 REAL,
    q3 REAL,
    q4 REAL,
    gt_year INTEGER,
    taken INTEGER,
    PRIMARY KEY (username, course, section)
)
""")
conn.commit()


# =============================
# HELPER FUNCTIONS
# =============================
def weighted_gpa(avg, weight):
    return max(weight - 0.1 * (100 - avg), 0)


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
    "AP Computer Science": 6.0,
    "Sports": 5.0,
    "Health": 5.0,
    "Computer Science": 5.5,
    "Instruments": 5.0
}

# =============================
# SESSION
# =============================
if "user" not in st.session_state:
    st.session_state.user = "Demo"  # Placeholder user

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

    selected_ms_courses = st.multiselect("Select Middle School Courses", list(courses.keys()))

    for course in selected_ms_courses:
        s1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, 90.0, key=f"ms_s1_{course}")
        s2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, 90.0, key=f"ms_s2_{course}")

        avg = (s1 + s2) / 2
        weight = courses[course] if courses[course] else 5.5  # Default weight for GT
        ms_course_gpas[course] = weighted_gpa(avg, weight)

# =============================
# HIGH SCHOOL
# =============================
with tabs[1]:
    st.header("High School Grades")
    hs_course_gpas = {}
    quarters = st.slider("Quarters Completed", 1, 4, 2)

    selected_hs_courses = st.multiselect("Select High School Courses", list(courses.keys()))

    gt_year = None
    if "GT / AP World History" in selected_hs_courses:
        gt_year = st.radio("GT / AP World Year?", [1, 2], horizontal=True)

    for course in selected_hs_courses:
        grades = []
        for i in range(quarters):
            grades.append(st.number_input(f"{course} – Quarter {i + 1}", 0.0, 100.0, 90.0, key=f"hs_q_{course}_{i}"))
        avg = sum(grades) / len(grades)
        weight = courses[course] if courses[course] else (5.5 if gt_year == 1 else 6.0)
        hs_course_gpas[course] = weighted_gpa(avg, weight)

# =============================
# GPA & ANALYTICS
# =============================
with tabs[2]:
    st.header("GPA Results & Analytics")
    if st.button("🎯 Calculate GPA"):
        all_gpas = list(ms_course_gpas.values()) + list(hs_course_gpas.values())
        if all_gpas:
            weighted_final = round(sum(all_gpas) / len(all_gpas), 2)
            unweighted_final = round(sum([unweighted_gpa(x) for x in all_gpas]) / len(all_gpas), 2)

            st.success(f"🎓 **Weighted GPA:** {weighted_final}")
            st.success(f"📘 **Unweighted GPA:** {unweighted_final}")

            # Analytics table
            st.subheader("📊 GPA by Class")
            st.write("**Middle School**")
            ms_table = {k: round(v, 2) for k, v in ms_course_gpas.items()}
            st.table(ms_table)
            st.write("**High School**")
            hs_table = {k: round(v, 2) for k, v in hs_course_gpas.items()}
            st.table(hs_table)

            # Best / worst impact
            combined = {**ms_course_gpas, **hs_course_gpas}
            if combined:
                best = max(combined, key=combined.get)
                worst = min(combined, key=combined.get)
                st.subheader("📈 Class Impact")
                st.write(f"✅ Highest GPA Impact: {best} → {combined[best]:.2f}")
                st.write(f"❌ Lowest GPA Impact: {worst} → {combined[worst]:.2f}")
        else:
            st.warning("No courses selected.")