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
# COURSES (Only the ones you mentioned)
# =============================
courses = [
    "Spanish 1",
    "Spanish 2",
    "Spanish 3",
    "Spanish 4 AP",
    "Algebra 1",
    "Geometry",
    "Algebra 2",
    "AP Precalculus",
    "GT Humanities / AP World",
    "Biology",
    "Chemistry",
    "AP Human Geography",
    "Sports",
    "AP Computer Science Principles",
    "Survey of Business Marketing Finance",
    "Health",
    "Computer Science",
    "Instruments"
]

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

    for course in courses:
        # Load previous grades
        c.execute("SELECT s1, s2 FROM grades WHERE section='MS' AND course=?", (course,))
        row = c.fetchone() or (90.0, 90.0)

        taken = st.checkbox(course, key=f"ms_take_{course}", value=True)

        if taken:
            s1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, row[0], key=f"ms_s1_{course}")
            s2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, row[1], key=f"ms_s2_{course}")
        else:
            s1, s2 = None, None

        # Save middle school grades
        c.execute("""
        INSERT OR REPLACE INTO grades
        (section, course, s1, s2, q1, q2, q3, q4, gt_year)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, ( "MS", course, s1, s2, None, None, None, None, None))
    conn.commit()

# -----------------------------
# HIGH SCHOOL
# -----------------------------
with tabs[1]:
    st.header("High School Grades")
    quarters = st.slider("Quarters Completed", 1, 4, 2)

    for course in courses:
        c.execute("SELECT q1,q2,q3,q4,gt_year FROM grades WHERE section='HS' AND course=?", (course,))
        row = c.fetchone() or (90.0, 90.0, 90.0, 90.0, None)

        taken = st.checkbox(course, key=f"hs_take_{course}", value=True)
        grades = []

        if taken:
            for i in range(quarters):
                grades.append(
                    st.number_input(f"{course} – Quarter {i+1}", 0.0, 100.0, row[i], key=f"hs_q_{course}_{i}")
                )

            # Special GT / AP World year selection
            gt_year = row[4]
            if course == "GT Humanities / AP World":
                gt_year = st.radio("Select GT/AP World Year", [1,2], index=0 if gt_year is None else gt_year-1, key="gt_year")
            else:
                gt_year = None
        else:
            grades = [None]*4
            gt_year = None

        padded = grades + [None]*(4 - len(grades))
        c.execute("""
        INSERT OR REPLACE INTO grades
        (section, course, s1, s2, q1, q2, q3, q4, gt_year)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, ("HS", course, None, None, *padded, gt_year))
    conn.commit()

# -----------------------------
# GPA & ANALYTICS
# -----------------------------
with tabs[2]:
    st.header("GPA Results & Analytics")

    if st.button("🎯 Calculate GPA"):
        weighted, unweighted = [], []

        for course in courses:
            c.execute("SELECT q1,q2,q3,q4,gt_year FROM grades WHERE section='HS' AND course=?", (course,))
            row = c.fetchone()

            if row:
                valid = [x for x in row[:4] if x is not None]
                if valid:
                    avg = sum(valid)/len(valid)
                    # weight GT/AP World depending on year
                    weight = 6.0 if course == "GT Humanities / AP World" and row[4]==2 else 5.5
                    weighted.append(weighted_gpa(avg, weight))
                    unweighted.append(unweighted_gpa(avg))

        if weighted:
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
        else:
            st.warning("No high school courses selected.")