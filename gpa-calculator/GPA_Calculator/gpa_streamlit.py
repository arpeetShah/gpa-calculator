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
    "GT Humanities / AP World": None,  # weight depends on year
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

    for course in ms_selected:
        c.execute("""
        SELECT s1, s2, gt_year, taken FROM grades
        WHERE username=? AND course=? AND section='MS'
        """, (st.session_state.user, course))
        row = c.fetchone() or (90.0, 90.0, None, 1)

        s1 = st.number_input(
            f"{course} – Semester 1",
            0.0, 100.0, row[0], key=f"ms_s1_{course}"
        )
        s2 = st.number_input(
            f"{course} – Semester 2",
            0.0, 100.0, row[1], key=f"ms_s2_{course}"
        )

        gt_year = row[2]
        if course == "GT Humanities / AP World":
            gt_year = st.radio("GT/AP World Year", [1, 2], index=(row[2] - 1 if row[2] else 0), horizontal=True)

        c.execute("""
        INSERT OR REPLACE INTO grades
        VALUES (?,?,?,?,?,?,?,?,?, ?, ?)
        """, (
            st.session_state.user, course, "MS",
            s1, s2, None, None, None, None,
            gt_year,
            1
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
        row = c.fetchone() or (90.0, 90.0, 90.0, 90.0, 1)

        grades = []
        for i in range(quarters):
            grades.append(
                st.number_input(
                    f"{course} – Quarter {i + 1}",
                    0.0, 100.0, row[i], key=f"hs_q_{course}_{i}"
                )
            )

        padded = grades + [None] * (4 - len(grades))

        c.execute("""
        INSERT OR REPLACE INTO grades
        VALUES (?,?,?,?,?,?,?,?,?, ?, ?)
        """, (
            st.session_state.user, course, "HS",
            None, None,
            *padded,
            None,
            1
        ))
    conn.commit()

# =============================
# GPA & ANALYTICS
# =============================
with tabs[2]:
    st.header("GPA Results & Analytics")

    if st.button("🎯 Calculate GPA"):
        weighted, unweighted = [], []

        for course, weight in courses.items():
            c.execute("""
            SELECT q1, q2, q3, q4, taken FROM grades
            WHERE username=? AND course=? AND section='HS'
            """, (st.session_state.user, course))
            row = c.fetchone()

            if row and row[4]:
                valid = [x for x in row[:4] if x is not None]

                if valid:
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