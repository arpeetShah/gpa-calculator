# redeploy trigger
import streamlit as st
import pandas as pd
import datetime
import sqlite3

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="EduPortal GPA Calculator",
    page_icon="📘",
    layout="wide",
)

# -----------------------------
# CUSTOM CSS (gradient background + bubble tabs)
# -----------------------------
st.markdown(
    """
    <style>
    /* Gradient background */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
    }

    /* Bubble tabs */
    .css-1hynsf2 {
        background-color: rgba(255,255,255,0.1);
        border-radius: 30px;
        padding: 10px 20px;
        margin: 5px;
    }
    </style>
    """, unsafe_allow_html=True
)

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect("gpa_users.db")
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    ms_grades TEXT
)
''')
conn.commit()

# -----------------------------
# SIMPLE USER PROFILE
# -----------------------------
def signup():
    st.subheader("Create Account")
    new_user = st.text_input("Username", key="signup_user")
    new_pass = st.text_input("Password", type="password", key="signup_pass")
    if st.button("Sign Up"):
        c.execute("SELECT * FROM users WHERE username=?", (new_user,))
        if c.fetchone():
            st.error("Username already exists!")
        else:
            c.execute("INSERT INTO users (username, password, ms_grades) VALUES (?, ?, ?)",
                      (new_user, new_pass, ""))
            conn.commit()
            st.success("Account created! Please login.")
            st.experimental_rerun()

def login():
    st.subheader("Login")
    user = st.text_input("Username", key="login_user")
    pw = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
        data = c.fetchone()
        if data:
            st.session_state.user = user
            st.success(f"Welcome, {user}!")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")

# -----------------------------
# LOGIN / SIGNUP FLOW
# -----------------------------
if "user" not in st.session_state:
    st.title("📘 EduPortal GPA Calculator")
    choice = st.radio("Select Option", ["Login", "Sign Up"])
    if choice == "Login":
        login()
    else:
        signup()
    st.stop()

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

# -----------------------------
# RETRIEVE MIDDLE SCHOOL DATA
# -----------------------------
c.execute("SELECT ms_grades FROM users WHERE username=?", (st.session_state.user,))
ms_data = c.fetchone()[0]
if ms_data:
    ms_grades_saved = eval(ms_data)
else:
    ms_grades_saved = {}

# -----------------------------
# TABS
# -----------------------------
tab_names = ["Middle School GPA", "High School GPA", "GPA Analytics"]
tabs = st.tabs(tab_names)

# -----------------------------
# MIDDLE SCHOOL GPA TAB
# -----------------------------
with tabs[0]:
    st.header("Middle School Grades")
    ms_selected = st.multiselect(
        "Select your Middle School courses",
        [f"{k}. {v[0]}" for k, v in courses.items()]
    )
    ms_weights = {}
    ms_input = {}
    for item in ms_selected:
        num = int(item.split(".")[0])
        name, base_weight = courses[num]
        weight = base_weight
        default_sem1 = ms_grades_saved.get(name, [90, 90])[0]
        default_sem2 = ms_grades_saved.get(name, [90, 90])[1]
        sem1 = st.number_input(f"{name} Semester 1", 0, 100, value=default_sem1, key=f"ms_{num}_1")
        sem2 = st.number_input(f"{name} Semester 2", 0, 100, value=default_sem2, key=f"ms_{num}_2")
        ms_input[name] = [sem1, sem2]
        ms_weights[name] = weight
    if st.button("Save Middle School Grades"):
        c.execute("UPDATE users SET ms_grades=? WHERE username=?",
                  (str(ms_input), st.session_state.user))
        conn.commit()
        st.success("Middle School grades saved!")

# -----------------------------
# HIGH SCHOOL GPA TAB
# -----------------------------
with tabs[1]:
    st.header("High School Grades")
    hs_selected = st.multiselect(
        "Select your High School courses",
        [f"{k}. {v[0]}" for k, v in courses.items()]
    )
    quarters_done = st.slider("How many quarters completed?", 1, 4, 2)
    hs_weights = {}
    hs_input = {}
    gt_year = None
    for item in hs_selected:
        num = int(item.split(".")[0])
        name, base_weight = courses[num]
        if num == 9:
            gt_year = st.radio("GT Humanities year", [1, 2], horizontal=True)
            weight = 5.5 if gt_year == 1 else 6.0
        else:
            weight = base_weight
        hs_weights[name] = weight
        hs_input[name] = []
        for q in range(1, quarters_done+1):
            hs_input[name].append(st.number_input(f"{name} Quarter {q}", 0, 100, 90, key=f"hs_{num}_{q}"))

# -----------------------------
# GPA ANALYTICS TAB
# -----------------------------
with tabs[2]:
    st.header("GPA Analytics")
    if st.button("Calculate GPA"):
        # Combine MS & HS
        all_weighted, all_unweighted = [], []
        avg_dict = {}

        for name, grades in ms_input.items():
            avg = sum(grades)/len(grades)
            all_weighted.append(weighted_gpa(avg, ms_weights[name]))
            all_unweighted.append(unweighted_gpa(avg))
            avg_dict[name] = avg

        for name, grades in hs_input.items():
            avg = sum(grades)/len(grades)
            all_weighted.append(weighted_gpa(avg, hs_weights[name]))
            all_unweighted.append(unweighted_gpa(avg))
            avg_dict[name] = avg

        weighted_final = round(sum(all_weighted)/len(all_weighted), 2) if all_weighted else 0
        unweighted_final = round(sum(all_unweighted)/len(all_unweighted), 2) if all_unweighted else 0

        st.success(f"🎯 Weighted GPA: {weighted_final}")
        st.success(f"📘 Unweighted GPA: {unweighted_final}")

        # Analytics
        st.subheader("Class Analysis")
        for name, avg in avg_dict.items():
            if avg >= 90:
                st.write(f"✅ {name} is boosting your GPA! (Avg: {avg})")
            elif avg >= 75:
                st.write(f"⚠️ {name} is okay but could improve. (Avg: {avg})")
            else:
                st.write(f"❌ {name} is lowering your GPA! (Avg: {avg})")

        # Save HS grades in session
        st.session_state.hs_input = hs_input