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
    gt_year INTEGER,
    PRIMARY KEY (course, section)
)
""")
conn.commit()

# =============================
# GPA FUNCTIONS
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
    "GT Humanities / AP World": None,
    "Biology": 5.5,
    "Chemistry": 5.5,
    "AP Human Geography": 6.0,
    "Sports": 5.0,
    "AP Computer Science Principles": 6.0,
    "Survey of Business Marketing Finance": 5.0,
    "Health": 5.0,
    "Computer Science": 5.5,
    "Instruments": 5.0
}

# =============================
# SESSION STATE
# =============================
if "ms_courses" not in st.session_state:
    st.session_state.ms_courses = []
if "hs_courses" not in st.session_state:
    st.session_state.hs_courses = []

# =============================
# MAIN APP
# =============================
st.title("🎓 EduSphere")
tabs = st.tabs(["🏫 Middle School", "🎓 High School", "📊 GPA & Analytics"])

# =============================
# MIDDLE SCHOOL TAB
# =============================
with tabs[0]:
    st.header("Middle School Grades")

    st.session_state.ms_courses = st.multiselect(
        "Select your Middle School courses:",
        list(courses.keys()),
        default=st.session_state.ms_courses
    )

    ms_course_gpas = {}

    for course in st.session_state.ms_courses:
        c.execute("SELECT s1, s2 FROM grades WHERE course=? AND section='MS'", (course,))
        row = c.fetchone() or (90.0, 90.0)

        s1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, row[0], key=f"ms_s1_{course}")
        s2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, row[1], key=f"ms_s2_{course}")

        avg = (s1 + s2) / 2
        weight = courses[course] if courses[course] is not None else 5.5
        ms_course_gpas[course] = weighted_gpa(avg, weight)

        c.execute("""
        INSERT OR REPLACE INTO grades
        (course, section, s1, s2, q1, q2, q3, q4, gt_year)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (course, "MS", s1, s2, None, None, None, None, None))
    conn.commit()

# =============================
# HIGH SCHOOL TAB
# =============================
with tabs[1]:
    st.header("High School Grades")
    quarters = st.slider("Quarters Completed", 1, 4, 2)

    st.session_state.hs_courses = st.multiselect(
        "Select your High School courses:",
        list(courses.keys()),
        default=st.session_state.hs_courses
    )

    hs_course_gpas = {}

    for course in st.session_state.hs_courses:
        c.execute("SELECT q1, q2, q3, q4, gt_year FROM grades WHERE course=? AND section='HS'", (course,))
        row = c.fetchone() or (90.0, 90.0, 90.0, 90.0, None)

        grades = []
        for i in range(quarters):
            grades.append(
                st.number_input(f"{course} – Quarter {i+1}", 0.0, 100.0, row[i], key=f"hs_q_{course}_{i}")
            )

        if course == "GT Humanities / AP World":
            gt_year = st.selectbox(f"{course} – Year", [1,2], index=row[4]-1 if row[4] else 0, key=f"gt_year")
        else:
            gt_year = None

        avg = sum(grades)/len(grades)
        weight = courses[course] if courses[course] is not None else 5.5
        hs_course_gpas[course] = weighted_gpa(avg, weight)

        padded = grades + [None]*(4 - len(grades))
        c.execute("""
        INSERT OR REPLACE INTO grades
        (course, section, s1, s2, q1, q2, q3, q4, gt_year)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (course, "HS", None, None, *padded, gt_year))
    conn.commit()

# =============================
# GPA & ANALYTICS TAB
# =============================
with tabs[2]:
    st.header("GPA Results & Analytics")
    if st.button("🎯 Calculate GPA"):
        # Weighted and unweighted GPA
        weighted_final = round(sum(ms_course_gpas.values() + hs_course_gpas.values()) /
                               (len(ms_course_gpas)+len(hs_course_gpas)), 2)
        unweighted_final = round(sum([unweighted_gpa(v) for v in ms_course_gpas.values()] +
                                     [unweighted_gpa(v) for v in hs_course_gpas.values()]) /
                                 (len(ms_course_gpas)+len(hs_course_gpas)), 2)

        st.success(f"🎓 **Weighted GPA:** {weighted_final}")
        st.success(f"📘 **Unweighted GPA:** {unweighted_final}")

        st.divider()
        st.subheader("📋 GPA by Class")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🏫 Middle School")
            if ms_course_gpas:
                st.table({
                    "Course": list(ms_course_gpas.keys()),
                    "GPA": [round(v,2) for v in ms_course_gpas.values()]
                })
        with col2:
            st.markdown("### 🎓 High School")
            if hs_course_gpas:
                st.table({
                    "Course": list(hs_course_gpas.keys()),
                    "GPA": [round(v,2) for v in hs_course_gpas.values()]
                })

        st.divider()
        st.subheader("📈 GPA Impact Analysis")
        if hs_course_gpas:
            best_course = max(hs_course_gpas, key=hs_course_gpas.get)
            worst_course = min(hs_course_gpas, key=hs_course_gpas.get)
            st.success(f"✅ **Helping Your GPA the Most:** {best_course} ({round(hs_course_gpas[best_course],2)})")
            st.warning(f"⚠️ **Bringing Your GPA Down the Most:** {worst_course} ({round(hs_course_gpas[worst_course],2)})")

        st.divider()
        st.subheader("🧠 Performance Insight")
        if weighted_final >= 5.5:
            st.write("🚀 Outstanding GPA, strong performance in weighted courses.")
        elif weighted_final >= 4.8:
            st.write("💪 Very strong GPA. Improving one high-impact class could push it higher.")
        elif weighted_final >= 4.0:
            st.write("📘 Solid GPA, some GPA-heavy classes pulling down performance.")
        else:
            st.write("🛠️ GPA is being pulled down by key courses. Focus on high-weight classes.")