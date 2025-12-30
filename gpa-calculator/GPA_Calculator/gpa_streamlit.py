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
    gt_year TEXT,
    taken INTEGER,
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
    "GT / AP World History": 6.0,
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
# SESSION
# =============================
if "user" not in st.session_state:
    st.session_state.user = "default_user"  # Temporary for testing without login

# =============================
# MAIN TOP-LEVEL TABS
# =============================
main_tabs = st.tabs(["🏠 Welcome", "🎓 GPA", "📝 Quiz & Practice"])

# =============================
# WELCOME TAB
# =============================
with main_tabs[0]:
    st.header("Welcome to EduSphere!")
    st.image(
        "https://images.unsplash.com/photo-1596496056730-3b7162c14d1c?auto=format&fit=crop&w=1200&q=80",
        use_column_width=True
    )
    st.write("Track your GPA, get insights, and practice quizzes all in one place.")

# =============================
# GPA TAB
# =============================
with main_tabs[1]:
    gpa_subtabs = st.tabs(["🏫 Middle School", "🎓 High School", "📊 GPA & Analytics"])

    # -----------------------------
    # MIDDLE SCHOOL
    # -----------------------------
    with gpa_subtabs[0]:
        st.header("Middle School Grades")
        ms_selected = st.multiselect(
            "Select the courses you took",
            options=list(courses.keys()),
            default=[]
        )

        ms_course_gpas = {}
        for course in ms_selected:
            s1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, 90.0, key=f"ms_s1_{course}")
            s2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, 90.0, key=f"ms_s2_{course}")
            avg = (s1 + s2) / 2
            ms_course_gpas[course] = avg

    # -----------------------------
    # HIGH SCHOOL
    # -----------------------------
    with gpa_subtabs[1]:
        st.header("High School Grades")
        quarters = st.slider("Quarters Completed", 1, 4, 2)
        hs_selected = st.multiselect(
            "Select the courses you took",
            options=list(courses.keys()),
            default=[]
        )

        hs_course_gpas = {}
        hs_gt_years = {}
        for course in hs_selected:
            grades = []
            for i in range(quarters):
                grades.append(
                    st.number_input(f"{course} – Quarter {i+1}", 0.0, 100.0, 90.0, key=f"hs_q_{course}_{i}")
                )
            padded = grades + [None] * (4 - len(grades))
            avg = sum([x for x in padded if x is not None]) / quarters
            hs_course_gpas[course] = avg

            if "GT / AP World History" in course:
                year = st.text_input(f"{course} Year Taken", key=f"gt_year_{course}")
                hs_gt_years[course] = year

    # -----------------------------
    # GPA & ANALYTICS
    # -----------------------------
    with gpa_subtabs[2]:
        st.header("GPA Results & Analytics")
        if st.button("🎯 Calculate GPA"):
            weighted_list, unweighted_list = [], []

            for course, weight in courses.items():
                if course in hs_course_gpas:
                    avg = hs_course_gpas[course]
                    weighted_list.append(weighted_gpa(avg, weight))
                    unweighted_list.append(unweighted_gpa(avg))
                elif course in ms_course_gpas:
                    avg = ms_course_gpas[course]
                    weighted_list.append(weighted_gpa(avg, weight))
                    unweighted_list.append(unweighted_gpa(avg))

            if not weighted_list:
                st.warning("No courses selected.")
            else:
                weighted_final = round(sum(weighted_list) / len(weighted_list), 2)
                unweighted_final = round(sum(unweighted_list) / len(unweighted_list), 2)

                st.success(f"🎓 Weighted GPA: {weighted_final}")
                st.success(f"📘 Unweighted GPA: {unweighted_final}")

                # Table of course GPAs
                st.subheader("Course GPAs")
                st.table({
                    "Middle School": ms_course_gpas,
                    "High School": hs_course_gpas
                })

                # Courses helping most and pulling down
                if weighted_list:
                    max_course = max(hs_course_gpas, key=lambda x: hs_course_gpas[x]) if hs_course_gpas else None
                    min_course = min(hs_course_gpas, key=lambda x: hs_course_gpas[x]) if hs_course_gpas else None
                    st.write(f"📈 Course helping GPA the most: {max_course}")
                    st.write(f"📉 Course bringing GPA down the most: {min_course}")

# =============================
# QUIZ TAB
# =============================
with main_tabs[2]:
    st.header("Quiz & Practice Problems")
    st.write("Here you can add quizzes, practice problems, or any interactive content for learning.")