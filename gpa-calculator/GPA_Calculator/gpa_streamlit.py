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
    course TEXT,
    section TEXT,
    s1 REAL,
    s2 REAL,
    q1 REAL,
    q2 REAL,
    q3 REAL,
    q4 REAL,
    taken INTEGER,
    gt_year TEXT,
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
    "AP Computer Science": 6.0,
    "Instruments": 5.0
}

# =============================
# TOP-LEVEL TABS
# =============================
top_tabs = st.tabs(["🏠 Welcome", "🎓 GPA", "📝 Quiz & Practice"])

# =============================
# WELCOME TAB
# =============================
with top_tabs[0]:
    st.title("🎉 Welcome to EduSphere!")
    st.write("Track your grades, analyze your GPA, and practice quizzes—all in one place.")
    # Updated image URL
    st.image("https://images.unsplash.com/photo-1596496052554-6f81b63b75b0?auto=format&fit=crop&w=800&q=60", use_column_width=True)

# =============================
# GPA TAB
# =============================
with top_tabs[1]:
    gpa_tabs = st.tabs(["🏫 Middle School", "🎓 High School", "📊 GPA & Analytics"])

    # =============================
    # MIDDLE SCHOOL
    # =============================
    with gpa_tabs[0]:
        st.header("Middle School Grades")

        ms_selected = st.multiselect(
            "Select the courses you took",
            options=list(courses.keys()),
            default=[]
        )

        for course in ms_selected:
            c.execute("""
            SELECT s1, s2, gt_year FROM grades
            WHERE course=? AND section='MS'
            """, (course,))
            row = c.fetchone() or (90.0, 90.0, "")

            s1 = st.number_input(
                f"{course} – Semester 1",
                0.0, 100.0, row[0], key=f"ms_s1_{course}"
            )
            s2 = st.number_input(
                f"{course} – Semester 2",
                0.0, 100.0, row[1], key=f"ms_s2_{course}"
            )

            # GT / AP World optional year
            gt_year = row[2]
            if course == "GT / AP World History":
                gt_year = st.text_input("GT / AP World History Year", value=row[2], key=f"ms_gt_{course}")

            c.execute("""
            INSERT OR REPLACE INTO grades
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                course, "MS", s1, s2, None, None, None, None, 1, gt_year
            ))
        conn.commit()

    # =============================
    # HIGH SCHOOL
    # =============================
    with gpa_tabs[1]:
        st.header("High School Grades")
        quarters = st.slider("Quarters Completed", 1, 4, 2)

        hs_selected = st.multiselect(
            "Select the courses you took",
            options=list(courses.keys()),
            default=[]
        )

        for course in hs_selected:
            c.execute("""
            SELECT q1, q2, q3, q4, gt_year FROM grades
            WHERE course=? AND section='HS'
            """, (course,))
            row = c.fetchone() or (90.0, 90.0, 90.0, 90.0, "")

            grades = []
            for i in range(quarters):
                grades.append(
                    st.number_input(
                        f"{course} – Quarter {i+1}",
                        0.0, 100.0, row[i],
                        key=f"hs_q_{course}_{i}"
                    )
                )

            padded = grades + [None]*(4 - len(grades))

            # GT / AP World optional year
            gt_year = row[4]
            if course == "GT / AP World History":
                gt_year = st.text_input("GT / AP World History Year", value=row[4], key=f"hs_gt_{course}")

            c.execute("""
            INSERT OR REPLACE INTO grades
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                course, "HS",
                None, None,
                *padded,
                1,
                gt_year
            ))
        conn.commit()

    # =============================
    # GPA & ANALYTICS
    # =============================
    with gpa_tabs[2]:
        st.header("GPA Results & Analytics")
        if st.button("🎯 Calculate GPA"):
            weighted, unweighted = [], []
            ms_course_gpas, hs_course_gpas = {}, {}

            for course, weight in courses.items():
                # Middle School
                c.execute("""
                SELECT s1, s2 FROM grades
                WHERE course=? AND section='MS'
                """, (course,))
                row = c.fetchone()
                if row:
                    valid = [x for x in row[:2] if x is not None]
                    if valid:
                        avg = sum(valid)/len(valid)
                        if weight:
                            weighted.append(weighted_gpa(avg, weight))
                        unweighted.append(unweighted_gpa(avg))
                        ms_course_gpas[course] = avg

                # High School
                c.execute("""
                SELECT q1, q2, q3, q4 FROM grades
                WHERE course=? AND section='HS'
                """, (course,))
                row = c.fetchone()
                if row:
                    valid = [x for x in row[:4] if x is not None]
                    if valid:
                        avg = sum(valid)/len(valid)
                        if weight:
                            weighted.append(weighted_gpa(avg, weight))
                        unweighted.append(unweighted_gpa(avg))
                        hs_course_gpas[course] = avg

            if not weighted:
                st.warning("No courses selected.")
            else:
                w = round(sum(weighted)/len(weighted), 2)
                uw = round(sum(unweighted)/len(unweighted), 2)
                st.success(f"🎓 **Weighted GPA:** {w}")
                st.success(f"📘 **Unweighted GPA:** {uw}")

                st.subheader("📊 GPA Insight")
                if w >= 5.5:
                    st.write("Your GPA is being boosted by strong performance in weighted courses.")
                elif w >= 4.5:
                    st.write("Your GPA is solid, but higher-weight classes have the biggest impact.")
                else:
                    st.write("Lower performance in GPA-heavy courses is pulling your GPA down.")

                st.subheader("📋 GPA Table")
                st.write("**Middle School:**")
                st.table(ms_course_gpas)
                st.write("**High School:**")
                st.table(hs_course_gpas)

                if hs_course_gpas:
                    max_class = max(hs_course_gpas, key=hs_course_gpas.get)
                    min_class = min(hs_course_gpas, key=hs_course_gpas.get)
                    st.write(f"📈 **Class Helping GPA Most:** {max_class}")
                    st.write(f"📉 **Class Bringing GPA Down Most:** {min_class}")

# =============================
# QUIZ & PRACTICE TAB
# =============================
with top_tabs[2]:
    st.header("Quiz & Practice Problems")
    st.write("Add your quizzes and practice problem features here.")