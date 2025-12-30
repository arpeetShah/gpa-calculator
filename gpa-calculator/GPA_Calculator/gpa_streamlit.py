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
    p1 REAL,
    p2 REAL,
    p3 REAL,
    p4 REAL,
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
                c.execute("INSERT INTO users VALUES (?,?)", (username, hash_pw(password)))
                conn.commit()
                st.success("Account created! Please login.")
    else:
        if st.button("Login"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?",
                      (username, hash_pw(password)))
            if c.fetchone():
                st.session_state.user = username
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

    st.stop()

# =============================
# MAIN
# =============================
st.title(f"👋 Welcome, {st.session_state.user}")
tabs = st.tabs(["🏫 Middle School", "🎓 High School", "📊 GPA & Analytics"])

# =============================
# MIDDLE SCHOOL
# =============================
with tabs[0]:
    st.header("Middle School Grades")

    for course in courses:
        c.execute("""
        SELECT p1, p2, taken FROM grades
        WHERE username=? AND course=? AND section="MS"
        """, (st.session_state.user, course))
        row = c.fetchone() or (90.0, 90.0, 0)

        taken = st.checkbox(f"{course}", value=bool(row[2]), key=f"ms_take_{course}")

        if taken:
            sem1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, row[0], key=f"ms1_{course}")
            sem2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, row[1], key=f"ms2_{course}")
        else:
            sem1, sem2 = None, None

        c.execute("""
        INSERT OR REPLACE INTO grades VALUES (?,?,?,?,?,?,?,?)
        """, (st.session_state.user, course, "MS", sem1, sem2, None, None, int(taken)))
    conn.commit()

# =============================
# HIGH SCHOOL
# =============================
with tabs[1]:
    st.header("High School Grades")
    quarters = st.slider("Quarters Completed", 1, 4, 2)

    for course in courses:
        c.execute("""
        SELECT p1, p2, p3, p4, taken FROM grades
        WHERE username=? AND course=? AND section="HS"
        """, (st.session_state.user, course))
        row = c.fetchone() or (90.0, 90.0, 90.0, 90.0, 0)

        taken = st.checkbox(f"{course}", value=bool(row[4]), key=f"hs_take_{course}")

        grades = []
        if taken:
            for i in range(quarters):
                grades.append(
                    st.number_input(
                        f"{course} – Quarter {i+1}",
                        0.0, 100.0, row[i],
                        key=f"hs_{course}_{i}"
                    )
                )

        padded = grades + [None] * (4 - len(grades))
        c.execute("""
        INSERT OR REPLACE INTO grades VALUES (?,?,?,?,?,?,?,?)
        """, (st.session_state.user, course, "HS", *padded, int(taken)))
    conn.commit()

# =============================
# GPA
# =============================
with tabs[2]:
    st.header("GPA Results & Analytics")

    if st.button("🎯 Calculate GPA"):
        weighted, unweighted = [], []

        for course, weight in courses.items():
            c.execute("""
            SELECT p1, p2, p3, p4, taken FROM grades
            WHERE username=? AND course=? AND section="HS"
            """, (st.session_state.user, course))
            row = c.fetchone()

            if row and row[4]:
                valid = [x for x in row[:4] if x is not