# redeploy trigger

import streamlit as st
import pandas as pd
import datetime
import json
import os

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="EduGPA",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# USER DATA STORAGE
# -----------------------------
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()
if "login" not in st.session_state:
    st.session_state.login = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

def toggle_form():
    st.session_state.show_signup = not st.session_state.show_signup

# -----------------------------
# LOGIN / SIGNUP
# -----------------------------
if not st.session_state.login:
    st.markdown(
        """
        <style>
        .main {
            background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
            color: white;
        }
        .stButton>button {
            background-color: #4b6cb7;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True
    )
    st.title("Welcome to EduGPA")
    st.write("Track your grades and GPA over time")

    if st.session_state.show_signup:
        st.subheader("📋 Sign Up")
        new_user = st.text_input("Username", key="signup_user")
        new_pass = st.text_input("Password", type="password", key="signup_pw")
        if st.button("Create Account"):
            if new_user in users:
                st.error("Username already exists!")
            else:
                users[new_user] = {"password": new_pass, "ms_grades": {}, "hs_grades": {}, "history": []}
                save_users(users)
                st.success("Account created! Please log in.")
        st.button("Already have an account? Login", on_click=toggle_form)
    else:
        st.subheader("🔑 Login")
        user = st.text_input("Username", key="login_user")
        pw = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            if user in users and users[user]["password"] == pw:
                st.session_state.login = True
                st.session_state.current_user = user
            else:
                st.error("Invalid credentials")
        st.button("Don't have an account? Sign Up", on_click=toggle_form)
    st.stop()

# -----------------------------
# GRADIENT STYLING
# -----------------------------
st.markdown(
    """
    <style>
    .stTabs [role="tablist"] button {
        border-radius: 50px;
        margin-right: 10px;
        padding: 0.5em 1.5em;
        font-weight: bold;
        background: linear-gradient(135deg, #0f2027, #2c5364);
        color: white;
    }
    .stTabs [role="tablist"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #4b6cb7, #182848);
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

def analyze_gpa(df):
    analysis = []
    for idx, row in df.iterrows():
        if row["Weighted GPA"] >= 5.8:
            analysis.append(f"{idx}: Excellent!")
        elif row["Weighted GPA"] >= 5.0:
            analysis.append(f"{idx}: Doing good")
        else:
            analysis.append(f"{idx}: Needs improvement")
    return analysis

# -----------------------------
# MAIN APP TABS
# -----------------------------
user_data = users[st.session_state.current_user]

tab1, tab2 = st.tabs(["📝 Middle School", "📚 High School"])

# -----------------------------
# MIDDLE SCHOOL TAB
# -----------------------------
with tab1:
    st.header("Middle School Grades")
    ms_courses = st.multiselect(
        "Select Middle School courses",
        [f"{k}. {v[0]}" for k, v in courses.items()],
        default=list(user_data.get("ms_grades", {}).keys())
    )
    ms_grades = user_data.get("ms_grades", {})

    for item in ms_courses:
        num = int(item.split(".")[0])
        name, base_weight = courses[num]
        weight = 5.5 if (num == 9 and ms_grades.get(name, {}).get("gt_year", 1) == 1) else 6.0 if num == 9 else base_weight
        if name not in ms_grades:
            ms_grades[name] = {"semester": 90, "gt_year": 1}
        if num == 9:
            ms_grades[name]["gt_year"] = st.radio(f"{name} - GT Year", [1, 2], horizontal=True, index=ms_grades[name]["gt_year"]-1, key=f"ms_gt_{num}")
            weight = 5.5 if ms_grades[name]["gt_year"] == 1 else 6.0
        ms_grades[name]["semester"] = st.number_input(f"{name} Semester grade", 0.0, 100.0, ms_grades[name]["semester"], key=f"ms_{num}")

    user_data["ms_grades"] = ms_grades
    save_users(users)

# -----------------------------
# HIGH SCHOOL TAB
# -----------------------------
with tab2:
    st.header("High School Grades")
    hs_courses = st.multiselect(
        "Select High School courses",
        [f"{k}. {v[0]}" for k, v in courses.items()],
        default=list(user_data.get("hs_grades", {}).keys())
    )
    hs_grades = user_data.get("hs_grades", {})
    quarters_done = st.slider("Quarters completed", 1, 4, 2)

    gt_year = None
    grades = {}

    for item in hs_courses:
        num = int(item.split(".")[0])
        name, base_weight = courses[num]
        if num == 9:
            gt_year = st.radio(f"{name} - GT Year", [1, 2], horizontal=True, key=f"hs_gt_{num}")
            weight = 5.5 if gt_year == 1 else 6.0
        else:
            weight = base_weight

        if name not in hs_grades:
            hs_grades[name] = [90.0] * quarters_done

        for q in range(quarters_done):
            if q < len(hs_grades[name]):
                hs_grades[name][q] = st.number_input(f"{name} Quarter {q+1}", 0.0, 100.0, hs_grades[name][q], key=f"hs_{num}_{q}")
            else:
                hs_grades[name].append(st.number_input(f"{name} Quarter {q+1}", 0.0, 100.0, 90.0, key=f"hs_{num}_{q}"))

        avg = sum(hs_grades[name])/len(hs_grades[name])
        grades[name] = {
            "Average": avg,
            "Weighted GPA": weighted_gpa(avg, weight),
            "Unweighted GPA": unweighted_gpa(avg)
        }

    user_data["hs_grades"] = hs_grades

    if st.button("📊 Calculate GPA"):
        df = pd.DataFrame(grades).T
        weighted_final = round(df["Weighted GPA"].mean(), 2)
        unweighted_final = round(df["Unweighted GPA"].mean(), 2)

        st.success(f"🎯 **Weighted GPA:** {weighted_final}")
        st.success(f"📘 **Unweighted GPA:** {unweighted_final}")

        st.subheader("📈 GPA Analysis")
        analysis = analyze_gpa(df)
        for line in analysis:
            st.write(line)

        record = {
            "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Weighted GPA": weighted_final,
            "Unweighted GPA": unweighted_final
        }
        user_data["history"].append(record)
        save_users(users)

# -----------------------------
# HISTORY DOWNLOAD
# -----------------------------
if user_data["history"]:
    st.header("🕒 GPA History")
    hist_df = pd.DataFrame(user_data["history"])
    st.dataframe(hist_df, use_container_width=True)

    csv = hist_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download GPA History", csv, "gpa_history.csv", "text/csv")