import streamlit as st
import pandas as pd
import json
import os
import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="EduGPA", page_icon="📘", layout="wide")

# -----------------------------
# UTILS
# -----------------------------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def weighted_gpa(avg, weight):
    return max(weight - ((100 - avg) * 0.1), 0)

def unweighted_gpa(avg):
    if avg >= 90: return 4
    if avg >= 80: return 3
    if avg >= 70: return 2
    if avg >= 60: return 1
    return 0

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
# STYLING
# -----------------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #0f2027, #2c3e50, #6a3093);
        color: #fff;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGIN / SIGNUP
# -----------------------------
users = load_users()
if "login" not in st.session_state:
    st.session_state.login = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

def signup():
    st.subheader("📋 Sign Up")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    if st.button("Create Account"):
        if new_user in users:
            st.error("Username already exists!")
        else:
            users[new_user] = {"password": new_pass, "ms_grades": {}, "hs_grades": {}, "history": []}
            save_users(users)
            st.success("Account created! Please log in.")

def login():
    st.subheader("🔑 Login")
    user = st.text_input("Username", key="login_user")
    pw = st.text_input("Password", type="password", key="login_pw")
    if st.button("Login"):
        if user in users and users[user]["password"] == pw:
            st.session_state.login = True
            st.session_state.current_user = user
        else:
            st.error("Invalid credentials")

if not st.session_state.login:
    st.title("Welcome to EduGPA")
    st.write("Sign up or login to track your grades and GPA")
    col1, col2 = st.columns(2)
    with col1: signup()
    with col2: login()
    st.stop()

# -----------------------------
# AFTER LOGIN
# -----------------------------
current_user = st.session_state.current_user
user_data = users[current_user]

st.title(f"Welcome, {current_user}!")

# -----------------------------
# TABS FOR MS AND HS
# -----------------------------
tabs = st.tabs(["🏫 Middle School", "🎓 High School", "📊 GPA Results"])

# -----------------------------
# MIDDLE SCHOOL INPUT
# -----------------------------
with tabs[0]:
    st.header("Middle School Grades")
    ms_grades = user_data.get("ms_grades", {})
    selected_ms = st.multiselect(
        "Select your Middle School courses",
        [f"{k}. {v[0]}" for k, v in courses.items()]
    )
    for item in selected_ms:
        num = int(item.split(".")[0])
        name, base_weight = courses[num]
        if num not in ms_grades:
            sem1 = st.number_input(f"{name} Semester 1", 0.0, 100.0, 90.0, key=f"ms_{num}_1")
            sem2 = st.number_input(f"{name} Semester 2", 0.0, 100.0, 90.0, key=f"ms_{num}_2")
            avg = (sem1 + sem2)/2
            weight = 5.5 if num == 9 else base_weight
            ms_grades[name] = {
                "Average": avg,
                "Weighted GPA": weighted_gpa(avg, weight),
                "Unweighted GPA": unweighted_gpa(avg)
            }
    user_data["ms_grades"] = ms_grades
    save_users(users)
    if ms_grades:
        df = pd.DataFrame(ms_grades).T
        st.dataframe(df)
        st.success("Middle School grades saved!")

# -----------------------------
# HIGH SCHOOL INPUT
# -----------------------------
with tabs[1]:
    st.header("High School Grades")
    hs_grades = user_data.get("hs_grades", {})
    selected_hs = st.multiselect(
        "Select your High School courses",
        [f"{k}. {v[0]}" for k, v in courses.items()]
    )
    quarters_done = st.slider("Quarters completed", 1, 4, 2)
    gt_year = None
    for item in selected_hs:
        num = int(item.split(".")[0])
        name, base_weight = courses[num]
        if num == 9:
            gt_year = st.radio("GT Humanities year", [1, 2], horizontal=True)
            weight = 5.5 if gt_year == 1 else 6.0
        else:
            weight = base_weight
        hs_grades[name] = {}
        for q in range(1, quarters_done+1):
            grade = st.number_input(f"{name} Quarter {q}", 0.0, 100.0, 90.0, key=f"hs_{num}_{q}")
            hs_grades[name][f"Q{q}"] = grade
        avg = sum(hs_grades[name].values()) / len(hs_grades[name])
        hs_grades[name]["Average"] = avg
        hs_grades[name]["Weighted GPA"] = weighted_gpa(avg, weight)
        hs_grades[name]["Unweighted GPA"] = unweighted_gpa(avg)
    user_data["hs_grades"] = hs_grades
    save_users(users)
    if hs_grades:
        df = pd.DataFrame(hs_grades).T
        st.dataframe(df)
        st.success("High School grades saved!")

# -----------------------------
# GPA RESULTS (only after button click)
# -----------------------------
with tabs[2]:
    st.header("📊 GPA Results")
    if st.button("📊 Calculate GPA"):
        weighted_final = None
        unweighted_final = None
        combined = {**ms_grades, **hs_grades}
        if combined:
            df = pd.DataFrame(combined).T
            weighted_final = round(df["Weighted GPA"].mean(), 2)
            unweighted_final = round(df["Unweighted GPA"].mean(), 2)
            st.success(f"🎯 **Weighted GPA:** {weighted_final}")
            st.success(f"📘 **Unweighted GPA:** {unweighted_final}")
            st.bar_chart(df[["Weighted GPA","Unweighted GPA"]])

            # Analytics
            top_course = df["Weighted GPA"].idxmax()
            bottom_course = df["Weighted GPA"].idxmin()
            st.subheader("📈 Analytics / Insights")
            st.markdown(f"- **Top contributor:** {top_course} ({df.loc[top_course,'Weighted GPA']} GPA)")
            st.markdown(f"- **Lowest contributor:** {bottom_course} ({df.loc[bottom_course,'Weighted GPA']} GPA)")

            # Save history
            if "history" not in user_data:
                user_data["history"] = []
            record = {
                "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Weighted GPA": weighted_final,
                "Unweighted GPA": unweighted_final
            }
            user_data["history"].append(record)
            users[current_user] = user_data
            save_users(users)

        # Show history
        if "history" in user_data and user_data["history"]:
            hist_df = pd.DataFrame(user_data["history"])
            st.subheader("🕒 GPA History")
            st.dataframe(hist_df)
            csv = hist_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download GPA History", csv, "gpa_history.csv", "text/csv")

# -----------------------------
# INSTALL TIP
# -----------------------------
st.info(
    "📱 **Install as app:**\n"
    "• iPhone: Safari → Share → Add to Home Screen\n"
    "• Android: Chrome → Add to Home Screen"
)