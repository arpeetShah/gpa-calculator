# redeploy trigger

import streamlit as st
import pandas as pd
import datetime
import sqlite3
import hashlib

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="EduGenius GPA Tracker",
    page_icon="📘",
    layout="wide",
)

# -----------------------------
# STYLING
# -----------------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #1e3c72, #2a5298, #6a3093);
        color: #fff;
    }
    .tab-button {
        border-radius: 20px !important;
        padding: 10px 20px;
        font-weight: bold;
        margin-right: 5px;
        background-color: rgba(255,255,255,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect("gpa_users.db")
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS grades (
        username TEXT,
        course TEXT,
        section TEXT,
        sem1 REAL,
        sem2 REAL,
        q1 REAL,
        q2 REAL,
        q3 REAL,
        q4 REAL,
        PRIMARY KEY(username, course, section)
    )
''')
conn.commit()

# -----------------------------
# COURSE LIST + WEIGHTS
# -----------------------------
courses = {
    1: ("Spanish 1", 5.0),
    2: ("Spanish 2", 5.0),
    3: ("Spanish 3", 5.5),
    4: ("Spanish 4 AP", 6.0),
    5: ("Algebra 1", 5.5),
    6: ("Geometry", 5.5),
    7: ("Algebra 2", 5.5),
    8: ("AP Precalculus", 6.0),
    9: ("GT Humanities / AP World", None),
    10: ("Biology", 5.5),
    11: ("Chemistry", 5.5),
    12: ("AP Human Geography", 6.0),
    13: ("Sports", 5.0),
    14: ("AP Computer Science Principles", 6.0),
    15: ("Survey of Business Marketing Finance", 5.0),
    16: ("Health", 5.0),
    17: ("Computer Science", 5.5),
    18: ("Instruments", 5.0)
}


# -----------------------------
# GPA FUNCTIONS
# -----------------------------
def weighted_gpa(avg, weight):
    return max(weight - ((100 - avg) * 0.1), 0)


def unweighted_gpa(avg):
    if avg >= 90: return 4
    if avg >= 80: return 3
    if avg >= 70: return 2
    if avg >= 60: return 1
    return 0


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# -----------------------------
# LOGIN / SIGNUP
# -----------------------------
st.title("📘 EduGenius GPA Tracker")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

auth_choice = st.radio("Login or Signup?", ["Login", "Signup"], horizontal=True)

username_input = st.text_input("Username")
password_input = st.text_input("Password", type="password")

if auth_choice == "Signup" and st.button("Create Account"):
    c.execute("SELECT * FROM users WHERE username=?", (username_input,))
    if c.fetchone():
        st.error("Username already exists!")
    else:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username_input, hash_password(password_input)))
        conn.commit()
        st.success("Account created! Please login.")
elif auth_choice == "Login" and st.button("Login"):
    c.execute("SELECT password FROM users WHERE username=?", (username_input,))
    record = c.fetchone()
    if record and record[0] == hash_password(password_input):
        st.session_state.logged_in = True
        st.session_state.username = username_input
        st.success(f"Welcome, {username_input}!")
    else:
        st.error("Invalid credentials.")

# -----------------------------
# MAIN APP
# -----------------------------
if st.session_state.logged_in:
    tab = st.selectbox("Choose tab", ["Middle School", "High School GPA"], index=0)

    username = st.session_state.username

    if tab == "Middle School":
        st.header("📝 Middle School Grades")
        ms_grades = {}
        for num, (name, base_weight) in courses.items():
            c.execute('SELECT sem1, sem2 FROM grades WHERE username=? AND course=? AND section="MS"', (username, name))
            row = c.fetchone()
            default_sem1 = row[0] if row else 90.0
            default_sem2 = row[1] if row else 90.0
            sem1 = st.number_input(f"{name} Semester 1", 0, 100, value=default_sem1, key=f"ms_{num}_1")
            sem2 = st.number_input(f"{name} Semester 2", 0, 100, value=default_sem2, key=f"ms_{num}_2)
            ms_grades[name] = (sem1, sem2)
            # Save to DB
            c.execute('INSERT OR REPLACE INTO grades (username, course, section, sem1, sem2) VALUES (?, ?, "MS", ?, ?)',
                      (username, name, sem1, sem2))
            conn.commit()

            elif tab == "High School GPA":
            st.header("📊 High School GPA Calculator")
            hs_selected = st.multiselect("Select your courses", [f"{k}. {v[0]}" for k, v in courses.items()])
            quarters_done = st.slider("How many quarters completed?", 1, 4, 2)
            weightages = {}
            grades_dict = {}

            for item in hs_selected:
                num = int(item.split(".")[0])
            name, base_weight = courses[num]
            if num == 9:
                gt_year = st.radio("GT Humanities Year", [1, 2], horizontal=True)
            weight = 5.5 if gt_year == 1 else 6.0
            else:
            weight = base_weight
            weightages[name] = weight

            qs = []
            for q in range(1, quarters_done + 1):
                qs.append(st.number_input(f"{name} Quarter {q}", 0, 100, 90, key=f"hs_{num}_{q}"))
            grades_dict[name] = qs

            if st.button("Calculate GPA"):
                results = {}
            for course, qs in grades_dict.items():
                avg = sum(qs) / len(qs)
            results[course] = {
                "Average": avg,
                "Weighted GPA": weighted_gpa(avg, weightages[course]),
                "Unweighted GPA": unweighted_gpa(avg)
            }
            df = pd.DataFrame(results).T
            weighted_final = round(df["Weighted GPA"].mean(), 2)
            unweighted_final = round(df["Unweighted GPA"].mean(), 2)
            st.success(f"Weighted GPA: {weighted_final}")
            st.success(f"Unweighted GPA: {unweighted_final}")

            st.subheader("GPA Analytics")
            for course, data in results.items():
                if
            data["Weighted GPA"] >= df["Weighted GPA"].mean():
            st.text(f"{course} is helping your GPA!")
            else:
            st.text(f"{course} is dragging your GPA down.")