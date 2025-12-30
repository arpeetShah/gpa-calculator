import streamlit as st
import sqlite3
import pandas as pd
import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="GPA Calculator",
    page_icon="📘",
    layout="wide"
)

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect('gpa_users.db', check_same_thread=False)
c = conn.cursor()

# Create users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
''')

# Create grades table
c.execute('''
CREATE TABLE IF NOT EXISTS grades (
    username TEXT,
    course TEXT,
    section TEXT,
    quarter INTEGER,
    grade REAL,
    PRIMARY KEY(username, course, section, quarter)
)
''')
conn.commit()

# -----------------------------
# COURSES & WEIGHTS
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

# -----------------------------
# LOGIN & SIGNUP
# -----------------------------
def signup():
    st.subheader("Sign Up")
    new_user = st.text_input("Username", key="signup_user")
    new_pass = st.text_input("Password", type="password", key="signup_pass")
    if st.button("Create Account"):
        if new_user and new_pass:
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_user, new_pass))
                conn.commit()
                st.success("Account created! Please login.")
            except:
                st.error("Username already exists!")

def login():
    st.subheader("Login")
    user = st.text_input("Username", key="login_user")
    pw = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
        if c.fetchone():
            st.session_state.logged_in = True
            st.session_state.username = user
        else:
            st.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if not st.session_state.logged_in:
    choice = st.radio("Select Option", ["Login", "Sign Up"])
    if choice == "Sign Up":
        signup()
    else:
        login()
    st.stop()

# -----------------------------
# GPA CALCULATOR TABS
# -----------------------------
st.title(f"Welcome, {st.session_state.username}!")

tab1, tab2 = st.tabs(["Middle School Grades", "High School Grades"])

# -----------------------------
# MIDDLE SCHOOL TAB
# -----------------------------
with tab1:
    st.header("Middle School Grades")
    ms_selected = st.multiselect("Select your Middle School courses", [v[0] for k,v in courses.items()])
    ms_data = {}
    for course in ms_selected:
        grade = st.number_input(f"{course} Semester Average", 0.0, 100.0, key=f"ms_{course}")
        ms_data[course] = grade
        # Save to DB
        c.execute("INSERT OR REPLACE INTO grades (username, course, section, quarter, grade) VALUES (?, ?, ?, ?, ?)",
                  (st.session_state.username, course, "MS", 1, grade))
    conn.commit()

# -----------------------------
# HIGH SCHOOL TAB
# -----------------------------
with tab2:
    st.header("High School Grades")
    hs_selected = st.multiselect("Select your High School courses", [v[0] for k,v in courses.items()])
    quarters_done = st.slider("How many quarters completed?", 1, 4, 2)
    hs_data = {}

    for course in hs_selected:
        weight = next((v[1] for k,v in courses.items() if v[0]==course), 5.5)
        qs = []
        for q in range(1, quarters_done+1):
            grade = st.number_input(f"{course} Quarter {q}", 0.0, 100.0, 90.0, key=f"hs_{course}_{q}")
            qs.append(grade)
            c.execute("INSERT OR REPLACE INTO grades (username, course, section, quarter, grade) VALUES (?, ?, ?, ?, ?)",
                      (st.session_state.username, course, "HS", q, grade))
        hs_data[course] = {
            "Average": sum(qs)/len(qs),
            "Weighted GPA": weighted_gpa(sum(qs)/len(qs), weight),
            "Unweighted GPA": unweighted_gpa(sum(qs)/len(qs))
        }
    conn.commit()

    if st.button("Calculate GPA"):
        df = pd.DataFrame(hs_data).T
        weighted_final = round(df["Weighted GPA"].mean(),2)
        unweighted_final = round(df["Unweighted GPA"].mean(),2)
        st.success(f"Weighted GPA: {weighted_final}")
        st.success(f"Unweighted GPA: {unweighted_final}")

        st.subheader("Analytics")
        best_courses = df[df["Weighted GPA"] > weighted_final].index.tolist()
        worst_courses = df[df["Weighted GPA"] < weighted_final].index.tolist()
        st.write("Doing well in:", best_courses)
        st.write("Needs improvement:", worst_courses)

        st.bar_chart(df[["Weighted GPA","Unweighted GPA"]])

# -----------------------------
# END OF APP
# -----------------------------