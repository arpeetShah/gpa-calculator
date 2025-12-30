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
    course TEXT,
    section TEXT,
    s1 REAL,
    s2 REAL,
    q1 REAL,
    q2 REAL,
    q3 REAL,
    q4 REAL,
    gt_year INTEGER
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
    # Languages
    "Spanish 1": 5.0,
    "Spanish 2": 5.0,
    "Spanish 3": 5.5,
    "Spanish 4 AP": 6.0,
    "French 1": 5.0,
    "French 2": 5.0,
    # Math
    "Algebra 1": 5.5,
    "Geometry": 5.5,
    "Algebra 2": 5.5,
    "AP Precalculus": 6.0,
    "Calculus AB": 6.0,
    "Calculus BC": 6.5,
    # Science
    "Biology": 5.5,
    "Chemistry": 5.5,
    "Physics": 5.5,
    "AP Biology": 6.0,
    "AP Chemistry": 6.0,
    "AP Physics": 6.0,
    # Social Studies
    "AP Human Geography": 6.0,
    "US History": 5.5,
    "World History": 5.5,
    "AP World History": 6.0,
    "GT Humanities / AP World": None,
    # Electives
    "Art 1": 5.0,
    "Art 2": 5.0,
    "Music 1": 5.0,
    "Music 2": 5.0
}

# =============================
# MAIN APP
# =============================
st.title("🎓 EduSphere")
tabs = st.tabs(["🏫 Middle School", "🎓 High School", "📊 GPA & Analytics"])

# =============================
# MIDDLE SCHOOL
# =============================
with tabs[0]:
    st.header("Middle School Grades")

    selected_ms = st.multiselect("Select your Middle School courses", list(courses.keys()), key="ms_dropdown")

    for course in selected_ms:
        c.execute("""
        SELECT s1, s2 FROM grades
        WHERE course=? AND section='MS'
        """, (course,))
        row = c.fetchone() or (90.0, 90.0)

        s1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, row[0], key=f"ms_s1_{course}")
        s2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, row[1], key=f"ms_s2_{course}")

        c.execute("""
        INSERT OR REPLACE INTO grades
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            course, "MS", s1, s2, None, None, None, None, None
        ))
    conn.commit()

# =============================
# HIGH SCHOOL
# =============================
with tabs[1]:
    st.header("High School Grades")
    selected_hs = st.multiselect("Select your High School courses", list(courses.keys()), key="hs_dropdown")
    quarters = st.slider("Quarters Completed", 1, 4, 2)

    for course in selected_hs:
        c.execute("""
        SELECT q1, q2, q3, q4, gt_year FROM grades
        WHERE course=? AND section='HS'
        """, (course,))
        row = c.fetchone() or (90.0, 90.0, 90.0, 90.0, None)

        grades = []
        for i in range(quarters):
            grades.append(
                st.number_input(
                    f"{course} – Quarter {i + 1}",
                    0.0, 100.0, row[i],
                    key=f"hs_q_{course}_{i}"
                )
            )

        # GT/AP World year selection
        gt_year = row[4]
        if course == "GT Humanities / AP World":
            gt_year = st.radio(f"{course} Year", [1, 2], index=0 if gt_year is None else gt_year - 1, key="gt_year")

        padded = grades + [None] * (4 - len(grades))

        c.execute("""
        INSERT OR REPLACE INTO grades
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            course, "HS", None, None, *padded, gt_year, None
        ))
    conn.commit()

# =============================
# GPA & ANALYTICS
# =============================
with tabs[2]:
    st.header("GPA Results & Analytics")

    if st.button("🎯 Calculate GPA"):
        weighted, unweighted = [], []

        for course in selected_hs:
            c.execute("""
            SELECT q1, q2, q3, q4, gt_year FROM grades
            WHERE course=? AND section='HS'
            """, (course,))
            row = c.fetchone()

            # Assign weight
            if course == "GT Humanities / AP World":
                if row[4] == 1:
                    weight = 5.5
                elif row[4] == 2:
                    weight = 6.0
                else:
                    weight = 5.5
            else:
                weight = courses.get(course)

            if row:
                valid = [x for x in row[:4] if x is not None]
                if valid and weight is not None:
                    avg = sum(valid) / len(valid)
                    weighted.append(weighted_gpa(avg, weight))
                    unweighted.append(unweighted_gpa(avg))

        if not weighted:
            st.warning("No high school courses selected.")
        else:
            w = round(sum(weighted) / len(weighted), 2)
            uw = round(sum(unweighted) / len(unweighted), 2)

            st.success(f"🎓 **Weighted GPA:** {w}")
            st.success(f"📘 **Unweighted GPA:** {uw}")

            st.subheader("📊 GPA Insight")
            if w >= 5.5:
                st.write("Your GPA is being boosted by strong performance in weighted courses.")
            elif w >= 4.5:
                st.write("Your GPA is solid, but higher-weight classes have the biggest impact.")
            else:
                st.write("Lower performance in GPA-heavy courses is pulling your GPA down.")