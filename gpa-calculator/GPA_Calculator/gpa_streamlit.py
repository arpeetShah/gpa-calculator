import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import datetime

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
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

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
# HELPERS
# =============================
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

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
    "AP Human Geography": 6.0
}

# =============================
# SESSION
# =============================
if "user" not in st.session_state:
    st.session_state.user = None

# =============================
# AUTH
# =============================
if not st.session_state.user:
    st.title("🎓 EduSphere")

    mode = st.radio("Welcome", ["Login", "Sign Up"], horizontal=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if mode == "Sign Up":
        if st.button("Create Account"):
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            if c.fetchone():
                st.error("Username already exists")
            else:
                c.execute(
                    "INSERT INTO users VALUES (?,?)",
                    (username, hash_pw(password))
                )
                conn.commit()
                st.success("Account created! Please login.")
    else:
        if st.button("Login"):
            c.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, hash_pw(password))
            )
            if c.fetchone():
                st.session_state.user = username
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

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
    ms_selected = st.multiselect("Select your Middle School courses", list(courses.keys()))
    gt_year = st.number_input("GT / AP World Year", min_value=1, max_value=2, value=1, step=1, key="gt_year_ms")

    for course in ms_selected:
        c.execute("""
        SELECT s1, s2, taken, gt_year FROM grades
        WHERE username=? AND course=? AND section='MS'
        """, (st.session_state.user, course))
        row = c.fetchone() or (90.0, 90.0, 0, gt_year)

        s1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, value=row[0], key=f"ms_s1_{course}")
        s2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, value=row[1], key=f"ms_s2_{course}")

        c.execute("""
        INSERT OR REPLACE INTO grades
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            st.session_state.user, course, "MS",
            s1, s2, None, None, None, None,
            1  # taken
        ))
    conn.commit()

# =============================
# HIGH SCHOOL
# =============================
with tabs[1]:
    st.header("High School Grades")
    quarters = st.slider("Quarters Completed", 1, 4, 2)
    hs_selected = st.multiselect("Select your High School courses", list(courses.keys()))

    for course in hs_selected:
        c.execute("""
        SELECT q1, q2, q3, q4, taken FROM grades
        WHERE username=? AND course=? AND section='HS'
        """, (st.session_state.user, course))
        row = c.fetchone() or (90.0, 90.0, 90.0, 90.0, 0)

        grades = []
        for i in range(quarters):
            grades.append(
                st.number_input(
                    f"{course} – Quarter {i+1}",
                    0.0, 100.0, value=row[i],
                    key=f"hs_q_{course}_{i}"
                )
            )
        padded = grades + [None] * (4 - len(grades))

        c.execute("""
        INSERT OR REPLACE INTO grades
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            st.session_state.user, course, "HS",
            None, None,
            *padded,
            1  # taken
        ))
    conn.commit()

# =============================
# GPA & ANALYTICS
# =============================
with tabs[2]:
    st.header("GPA Results & Analytics")
    if st.button("🎯 Calculate GPA"):

        # Combine MS and HS for chart
        gpa_history = []

        # Middle School GPA
        ms_weighted, ms_unweighted = [], []
        for course in ms_selected:
            c.execute("""
            SELECT s1, s2, gt_year FROM grades
            WHERE username=? AND course=? AND section='MS'
            """, (st.session_state.user, course))
            row = c.fetchone()
            if row:
                avg = (row[0] + row[1]) / 2
                ms_weighted.append(weighted_gpa(avg, courses[course]))
                ms_unweighted.append(unweighted_gpa(avg))
                gpa_history.append({'Term': f"MS {course} Sem1", 'Weighted': weighted_gpa(row[0], courses[course]), 'Unweighted': unweighted_gpa(row[0])})
                gpa_history.append({'Term': f"MS {course} Sem2", 'Weighted': weighted_gpa(row[1], courses[course]), 'Unweighted': unweighted_gpa(row[1])})

        # High School GPA
        hs_weighted, hs_unweighted = [], []
        for course in hs_selected:
            c.execute("""
            SELECT q1, q2, q3, q4 FROM grades
            WHERE username=? AND course=? AND section='HS'
            """, (st.session_state.user, course))
            row = c.fetchone()
            if row:
                valid = [x for x in row if x is not None]
                avg = sum(valid) / len(valid)
                hs_weighted.append(weighted_gpa(avg, courses[course]))
                hs_unweighted.append(unweighted_gpa(avg))
                for i, grade in enumerate(valid):
                    gpa_history.append({'Term': f"HS {course} Q{i+1}", 'Weighted': weighted_gpa(grade, courses[course]), 'Unweighted': unweighted_gpa(grade)})

        # Final GPA
        all_weighted = ms_weighted + hs_weighted
        all_unweighted = ms_unweighted + hs_unweighted

        if all_weighted:
            w_final = round(sum(all_weighted)/len(all_weighted), 2)
            uw_final = round(sum(all_unweighted)/len(all_unweighted), 2)
            st.success(f"🎓 Weighted GPA: {w_final}")
            st.success(f"📘 Unweighted GPA: {uw_final}")

            # Chart
            df = pd.DataFrame(gpa_history)
            st.subheader("📈 GPA Over Time")
            st.line_chart(df.set_index("Term")[["Weighted", "Unweighted"]])

            # Feedback
            st.subheader("📊 GPA Insight")
            if w_final >= 5.5:
                st.write("Your GPA is strong and being boosted by weighted courses!")
            elif w_final >= 4.5:
                st.write("Your GPA is solid. Weighted courses have the biggest impact.")
            else:
                st.write("Your GPA is lower; focus on key courses to improve!")

            # Export
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download GPA Report",
                csv,
                "gpa_report.csv",
                "text/csv"
            )
        else:
            st.warning("No courses selected to calculate GPA.")