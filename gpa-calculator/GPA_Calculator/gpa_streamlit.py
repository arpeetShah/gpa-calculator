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
# STYLES (UNCHANGED)
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
    "Biology": 5.5,
    "Chemistry": 5.5,
    "AP Human Geography": 6.0,
    "Sports": 5.0,
    "AP Computer Science Principles": 6.0,
    "Survey of Business Marketing Finance": 5.0,
    "Health": 5.0,
    "Computer Science": 5.5,
    "Instruments": 5.0,
    "GT Humanities / AP World": None
}

# =============================
# SESSION
# =============================
if "user" not in st.session_state:
    st.session_state.user = "Anonymous"  # dummy user for now since login is removed

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
    for course in courses:
        # Get saved grades if exist
        c.execute("""
        SELECT s1, s2, taken FROM grades
        WHERE username=? AND course=? AND section='MS'
        """, (st.session_state.user, course))
        row = c.fetchone() or (90.0, 90.0, 0)

        taken = st.checkbox(course, value=bool(row[2]), key=f"ms_take_{course}")

        if taken:
            s1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, row[0], key=f"ms_s1_{course}")
            s2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, row[1], key=f"ms_s2_{course}")
            avg = (s1 + s2) / 2
            ms_course_gpas[course] = avg
        else:
            s1, s2 = None, None

        # Save to database
        c.execute("""
        INSERT OR REPLACE INTO grades
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            st.session_state.user, course, "MS",
            s1, s2, None, None, None, None,
            int(taken), None
        ))
    conn.commit()

# =============================
# HIGH SCHOOL
# =============================
with tabs[1]:
    st.header("High School Grades")
    hs_course_gpas = {}
    quarters = st.slider("Quarters Completed", 1, 4, 2)

    for course, weight in courses.items():
        c.execute("""
        SELECT q1, q2, q3, q4, taken, gt_year FROM grades
        WHERE username=? AND course=? AND section='HS'
        """, (st.session_state.user, course))
        row = c.fetchone() or (90.0, 90.0, 90.0, 90.0, 0, None)

        taken = st.checkbox(course, value=bool(row[4]), key=f"hs_take_{course}")

        grades = []
        if taken:
            for i in range(quarters):
                grades.append(st.number_input(f"{course} – Quarter {i+1}", 0.0, 100.0, row[i], key=f"hs_q_{course}_{i}"))
            avg = sum(grades) / len(grades)
            hs_course_gpas[course] = avg

        padded = grades + [None] * (4 - len(grades))

        # GT/AP World year
        gt_year = None
        if course == "GT Humanities / AP World" and taken:
            gt_year = st.radio("GT/AP World Year", [1, 2], horizontal=True, key="gt_year")

        c.execute("""
        INSERT OR REPLACE INTO grades
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            st.session_state.user, course, "HS",
            None, None,
            *padded,
            int(taken),
            gt_year
        ))
    conn.commit()

# =============================
# GPA & ANALYTICS
# =============================
with tabs[2]:
    st.header("GPA Results & Analytics")

    if st.button("🎯 Calculate GPA"):
        # Combine MS and HS GPAs correctly
        all_gp_as = list(ms_course_gpas.values()) + list(hs_course_gpas.values())
        if not all_gp_as:
            st.warning("No courses selected.")
        else:
            weighted_list = []
            for course, gpa_avg in ms_course_gpas.items():
                weighted_list.append(weighted_gpa(gpa_avg, courses[course]))
            for course, gpa_avg in hs_course_gpas.items():
                weighted_list.append(weighted_gpa(gpa_avg, courses[course]))

            unweighted_list = [unweighted_gpa(x) for x in all_gp_as]

            weighted_final = round(sum(weighted_list) / len(weighted_list), 2)
            unweighted_final = round(sum(unweighted_list) / len(unweighted_list), 2)

            st.success(f"🎓 Weighted GPA: {weighted_final}")
            st.success(f"📘 Unweighted GPA: {unweighted_final}")

            # Analytics Table
            st.subheader("📊 GPA Breakdown per Course")
            table_data = []
            for course, gpa_avg in ms_course_gpas.items():
                table_data.append([course, "Middle School", round(gpa_avg, 2)])
            for course, gpa_avg in hs_course_gpas.items():
                table_data.append([course, "High School", round(gpa_avg, 2)])
            st.table(table_data)

            # Most positive and negative impact
            all_weighted = {}
            for course, gpa_avg in ms_course_gpas.items():
                all_weighted[course] = weighted_gpa(gpa_avg, courses[course])
            for course, gpa_avg in hs_course_gpas.items():
                all_weighted[course] = weighted_gpa(gpa_avg, courses[course])

            best_course = max(all_weighted, key=all_weighted.get)
            worst_course = min(all_weighted, key=all_weighted.get)
            st.subheader("🏆 Impact Analysis")
            st.write(f"Most positively impacting GPA: {best_course}")
            st.write(f"Most negatively impacting GPA: {worst_course}")