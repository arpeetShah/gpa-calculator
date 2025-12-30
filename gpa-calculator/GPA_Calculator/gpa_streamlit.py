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
        "Hey! I created this app/website for YOU to have a convenitent way to track your educational path. There is not platform(until now) which allows you to get your CUMMALITIVE GPA and that was the inspiration of this. Throughout this app, you can track your GPA, analyze it, and practice quizzes to improve your learning! Addtitionally, you do not need to give any personal credentials as you just manually input all of your grades and no one (including me) will have access to your personal information and grades.")
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
    st.write("This section is under development. Soon you will be able to take quizzes and practice problems!")