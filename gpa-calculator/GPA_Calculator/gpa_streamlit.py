# GPA Calculator Modernized with Tabs, Gradient Background, and Login

import streamlit as st
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
# GRADIENT BACKGROUND
# -----------------------------
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to right, #a1c4fd, #c2e9fb);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    .stDownloadButton>button {
        background-color: #1f77b4;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True
)

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
# LOGIN / SIGNUP
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {}  # username: password

if not st.session_state.logged_in:
    st.title("📘 GPA Calculator Login / Sign Up")

    option = st.radio("Choose:", ["Login", "Sign Up"], horizontal=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        if option == "Sign Up":
            if username in st.session_state.users:
                st.error("Username already exists")
            else:
                st.session_state.users[username] = password
                st.success("Sign up successful! Please login.")
        else:  # Login
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
            else:
                st.error("Incorrect username or password")

if st.session_state.logged_in:
    st.title(f"📘 Welcome, {st.session_state.user}!")

    # -----------------------------
    # TAB LAYOUT
    # -----------------------------
    tabs = st.tabs(["Middle School Grades", "High School Grades", "GPA Results"])

    # -----------------------------
    # MIDDLE SCHOOL TAB
    # -----------------------------
    with tabs[0]:
        st.header("📝 Middle School Grades")
        ms_grades = {}
        ms_courses_selected = st.multiselect(
            "Select Middle School Courses",
            [f"{k}. {v[0]}" for k, v in courses.items()]
        )
        for item in ms_courses_selected:
            num = int(item.split(".")[0])
            name, base_weight = courses[num]
            if num == 9:
                gt_year = st.radio(f"{name} year?", [1, 2], horizontal=True)
                weight = 5.5 if gt_year == 1 else 6.0
            else:
                weight = base_weight
            sem = st.number_input(f"{name} Semester Average", 0.0, 100.0, 90.0, key=f"ms_{num}")
            ms_grades[name] = {
                "Average": sem,
                "Weighted GPA": weighted_gpa(sem, weight),
                "Unweighted GPA": unweighted_gpa(sem)
            }

    # -----------------------------
    # HIGH SCHOOL TAB
    # -----------------------------
    with tabs[1]:
        st.header("📝 High School Grades")
        hs_grades = {}
        hs_courses_selected = st.multiselect(
            "Select High School Courses",
            [f"{k}. {v[0]}" for k, v in courses.items()]
        )
        quarters_done = st.slider("How many quarters completed?", 1, 4, 2)
        for item in hs_courses_selected:
            num = int(item.split(".")[0])
            name, base_weight = courses[num]
            if num == 9:
                gt_year = st.radio(f"{name} year?", [1, 2], horizontal=True)
                weight = 5.5 if gt_year == 1 else 6.0
            else:
                weight = base_weight
            qs = []
            for q in range(1, quarters_done + 1):
                qs.append(st.number_input(f"{name} Quarter {q}", 0.0, 100.0, 90.0, key=f"hs_{num}_{q}"))
            avg = sum(qs) / len(qs)
            hs_grades[name] = {
                "Average": avg,
                "Weighted GPA": weighted_gpa(avg, weight),
                "Unweighted GPA": unweighted_gpa(avg)
            }

    # -----------------------------
    # GPA RESULTS TAB
    # -----------------------------
    with tabs[2]:
        st.header("📊 GPA Results")
        combined = {**ms_grades, **hs_grades}
        if combined:
            df = pd.DataFrame(combined).T
            weighted_final = round(df["Weighted GPA"].mean(), 2)
            unweighted_final = round(df["Unweighted GPA"].mean(), 2)
            st.success(f"🎯 **Weighted GPA:** {weighted_final}")
            st.success(f"📘 **Unweighted GPA:** {unweighted_final}")
            st.bar_chart(df[["Weighted GPA", "Unweighted GPA"]])
        else:
            st.info("Select courses in the tabs above to see GPA results")