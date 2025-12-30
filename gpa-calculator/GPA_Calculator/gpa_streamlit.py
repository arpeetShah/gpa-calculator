# -----------------------------
# GPA Calculator with Persistent Database
# -----------------------------
import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import datetime

# -----------------------------
# DATABASE SETUP
# -----------------------------
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
    ms_sem1 REAL,
    ms_sem2 REAL,
    hs_quarters TEXT,
    PRIMARY KEY(username, course)
)
""")
conn.commit()


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_user(username, password):
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    return row and row[0] == hash_password(password)


def save_grades(username, ms_input, hs_input):
    for name, (sem1, sem2) in ms_input.items():
        c.execute("INSERT OR REPLACE INTO grades (username, course, ms_sem1, ms_sem2, hs_quarters) VALUES (?,?,?,?,?)",
                  (username, name, sem1, sem2, ""))
    for name, quarters in hs_input.items():
        quarters_str = ",".join(map(str, quarters))
        c.execute("INSERT OR REPLACE INTO grades (username, course, ms_sem1, ms_sem2, hs_quarters) VALUES (?,?,?,?,?)",
                  (username, name, None, None, quarters_str))
    conn.commit()


def load_grades(username):
    c.execute("SELECT course, ms_sem1, ms_sem2, hs_quarters FROM grades WHERE username = ?", (username,))
    rows = c.fetchall()
    ms_input, hs_input = {}, {}
    for course, sem1, sem2, hs_q in rows:
        if sem1 is not None and sem2 is not None:
            ms_input[course] = [sem1, sem2]
        if hs_q:
            hs_input[course] = list(map(float, hs_q.split(",")))
    return ms_input, hs_input


def weighted_gpa(avg, weight):
    return max(weight - ((100 - avg) * 0.1), 0)


def unweighted_gpa(avg):
    if avg >= 90: return 4
    if avg >= 80: return 3
    if avg >= 70: return 2
    if avg >= 60: return 1
    return 0


# -----------------------------
# PAGE CONFIG AND STYLING
# -----------------------------
st.set_page_config(page_title="GPA_Calculator", page_icon="📘", layout="wide")
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    color: white;
}
.stButton>button {
    background-color: #444; color: white; border-radius: 10px; padding: 8px 20px;
}
.tab-button {
    background-color: #444; border-radius: 30px; padding: 8px 16px; margin: 4px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# COURSE LIST + WEIGHTS
# -----------------------------
courses = {
    "Spanish 1": 5.0, "Spanish 2": 5.0, "Spanish 3": 5.5, "Spanish 4 AP": 6.0,
    "Algebra 1": 5.5, "Geometry": 5.5, "Algebra 2": 5.5, "AP Precalculus": 6.0,
    "GT Humanities / AP World": 6.0, "Biology": 5.5, "Chemistry": 5.5,
    "AP Human Geography": 6.0, "Sports": 5.0, "AP Computer Science Principles": 6.0,
    "Survey of Business Marketing Finance": 5.0, "Health": 5.0, "Computer Science": 5.5,
    "Instruments": 5.0
}

# -----------------------------
# LOGIN / SIGNUP
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    page = st.radio("Choose Page", ["Login", "Sign Up"], index=0, horizontal=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if page == "Sign Up":
        if st.button("Create Account"):
            c.execute("SELECT username FROM users WHERE username = ?", (username,))
            if c.fetchone():
                st.warning("Username already exists.")
            else:
                c.execute("INSERT INTO users (username, password) VALUES (?,?)",
                          (username, hash_password(password)))
                conn.commit()
                st.success("Account created! Please login.")
    else:
        if st.button("Login"):
            if check_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid credentials")

# -----------------------------
# MAIN APP AFTER LOGIN
# -----------------------------
if st.session_state.logged_in:
    st.title(f"Welcome, {st.session_state.username}")
    ms_input, hs_input = load_grades(st.session_state.username)

    tabs = st.tabs(["Middle School Grades", "High School Grades", "GPA Analytics"])

    # Middle School Tab
    with tabs[0]:
        st.header("Middle School Grades (2 Semesters)")
        for course, weight in courses.items():
            default_sem1 = ms_input.get(course, [0, 0])[0] if course in ms_input else 0
            default_sem2 = ms_input.get(course, [0, 0])[1] if course in ms_input else 0
            sem1 = st.number_input(f"{course} Semester 1", 0, 100, value=default_sem1, key=f"ms_{course}_1")
            sem2 = st.number_input(f"{course} Semester 2", 0, 100, value=default_sem2, key=f"ms_{course}_2")
            ms_input[course] = [sem1, sem2]

    # High School Tab
    with tabs[1]:
        st.header("High School Grades (Quarters)")
        quarters_done = st.slider("How many quarters completed?", 1, 4, 2)
        for course, weight in courses.items():
            default_hs = hs_input.get(course, [0] * quarters_done)
            hs_quarters = []
            for q in range(quarters_done):
                grade = st.number_input(f"{course} Q{q + 1}", 0, 100, value=default_hs[q] if q < len(default_hs) else 0,
                                        key=f"hs_{course}_{q + 1}")
                hs_quarters.append(grade)
            hs_input[course] = hs_quarters

    # GPA Analytics Tab
    with tabs[2]:
        st.header("GPA Analytics")
        if st.button("Calculate GPA"):
            save_grades(st.session_state.username, ms_input, hs_input)
            all_weighted, all_unweighted = [], []
            weighted_dict = {}

            # Middle School GPA
            for name, (sem1, sem2) in ms_input.items():
                avg = (sem1 + sem2) / 2
                w_gpa = weighted_gpa(avg, courses[name])
                all_weighted.append(w_gpa)
                all_unweighted.append(unweighted_gpa(avg))
                weighted_dict[name] = w_gpa

            # High School GPA
            for name, quarters in hs_input.items():
                avg = sum(quarters) / len(quarters)
                w_gpa = weighted_gpa(avg, courses[name])
                all_weighted.append(w_gpa)
                all_unweighted.append(unweighted_gpa(avg))
                weighted_dict[name] = w_gpa

            weighted_final = round(sum(all_weighted) / len(all_weighted), 2)
            unweighted_final = round(sum(all_unweighted) / len(all_unweighted), 2)

            st.success(f"🎯 Weighted GPA: {weighted_final}")
            st.success(f"📘 Unweighted GPA: {unweighted_final}")

            st.subheader("Class Analysis by GPA Impact")
            for name, w_gpa in weighted_dict.items():
                if w_gpa >= 5.5:
                    st.markdown(f"✅ **{name}** is boosting your GPA! (Weighted GPA: {w_gpa})")
                elif w_gpa >= 4.0:
                    st.markdown(f"⚠️ **{name}** is okay but could improve. (Weighted GPA: {w_gpa})")
                else:
                    st.markdown(f"❌ **{name}** is lowering your GPA! (Weighted GPA: {w_gpa})")