import streamlit as st
import pandas as pd
import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="GPA_Calculator",
    page_icon="📘",
    layout="centered"
)

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "users" not in st.session_state:
    st.session_state.users = {}  # {username: {"password":..., "ms_grades": {...}}}

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# WELCOME / SIGN UP / LOGIN
# -----------------------------
if st.session_state.current_user is None:
    st.title("📘 Welcome to GPA Calculator")

    choice = st.radio("Login or Sign Up", ["Login", "Sign Up"])

    if choice == "Sign Up":
        st.subheader("Create a new account")
        new_user = st.text_input("Username", key="signup_user")
        new_pass = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            if new_user in st.session_state.users:
                st.error("Username already exists.")
            elif new_user == "" or new_pass == "":
                st.warning("Please enter a username and password.")
            else:
                st.session_state.users[new_user] = {"password": new_pass, "ms_grades": {}}
                st.success("Account created! Please log in now.")
    else:  # Login
        st.subheader("Login to your account")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if login_user in st.session_state.users and st.session_state.users[login_user]["password"] == login_pass:
                st.session_state.current_user = login_user
                st.success(f"Welcome back {login_user}!")
            else:
                st.error("Incorrect username or password")

    st.stop()  # Stop execution until user logs in

# -----------------------------
# USER IS LOGGED IN
# -----------------------------
user = st.session_state.current_user
st.title(f"📘 GPA Calculator ({user})")

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
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["Middle School", "High School"])

# -----------------------------
# MIDDLE SCHOOL TAB
# -----------------------------
with tab1:
    st.header("🏫 Middle School Grades")
    selected_ms = st.multiselect(
        "Select your Middle School courses",
        [f"{k}. {v[0]}" for k, v in courses.items()]
    )

    ms_storage = st.session_state.users[user]["ms_grades"]

    for item in selected_ms:
        num = int(item.split(".")[0])
        name, base_weight = courses[num]

        if num in ms_storage:
            sem1 = st.number_input(f"{name} Semester 1 grade",
                                   value=ms_storage[num]["sem1"],
                                   key=f"ms_{num}_1")
            sem2 = st.number_input(f"{name} Semester 2 grade",
                                   value=ms_storage[num]["sem2"],
                                   key=f"ms_{num}_2")
        else:
            sem1 = st.number_input(f"{name} Semester 1 grade", 0.0, 100.0, 90.0,
                                   key=f"ms_{num}_1")
            sem2 = st.number_input(f"{name} Semester 2 grade", 0.0, 100.0, 90.0,
                                   key=f"ms_{num}_2")

        ms_storage[num] = {"sem1": sem1, "sem2": sem2}

# -----------------------------
# HIGH SCHOOL TAB
# -----------------------------
with tab2:
    st.header("📚 High School Grades")
    selected_hs = st.multiselect(
        "Select your High School courses",
        [f"{k}. {v[0]}" for k, v in courses.items()]
    )

    quarters_done = st.slider("How many quarters completed?", 1, 4, 2)
    gt_year = None
    hs_grades = {}

    for item in selected_hs:
        num = int(item.split(".")[0])
        name, base_weight = courses[num]

        if num == 9:
            gt_year = st.radio("GT Humanities year", [1, 2], horizontal=True)
            weight = 5.5 if gt_year == 1 else 6.0
        else:
            weight = base_weight

        qs = []
        for q in range(1, quarters_done + 1):
            qs.append(
                st.number_input(
                    f"{name} Quarter {q} grade",
                    0.0, 100.0, 90.0,
                    key=f"hs_{num}_{q}"
                )
            )

        avg = sum(qs) / len(qs)
        hs_grades[name] = {
            "Average": avg,
            "Weighted GPA": weighted_gpa(avg, weight),
            "Unweighted GPA": unweighted_gpa(avg)
        }

# -----------------------------
# CALCULATE BUTTON
# -----------------------------
if st.button("📊 Calculate GPA", use_container_width=True):
    all_grades = {}

    # Add Middle School grades
    for num, g in ms_storage.items():
        name, base_weight = courses[num]
        avg = (g["sem1"] + g["sem2"]) / 2
        all_grades[name] = {
            "Average": avg,
            "Weighted GPA": weighted_gpa(avg, base_weight),
            "Unweighted GPA": unweighted_gpa(avg)
        }

    # Add High School grades
    all_grades.update(hs_grades)

    if not all_grades:
        st.warning("Please input at least one grade.")
    else:
        df = pd.DataFrame(all_grades).T
        weighted_final = round(df["Weighted GPA"].mean(), 2)
        unweighted_final = round(df["Unweighted GPA"].mean(), 2)

        st.success(f"🎯 **Weighted GPA:** {weighted_final}")
        st.success(f"📘 **Unweighted GPA:** {unweighted_final}")

        st.subheader("📈 GPA Breakdown")
        st.bar_chart(df[["Weighted GPA", "Unweighted GPA"]])

        # Save history
        record = {
            "User": user,
            "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Weighted GPA": weighted_final,
            "Unweighted GPA": unweighted_final
        }
        st.session_state.history.append(record)

# -----------------------------
# HISTORY + DOWNLOAD
# -----------------------------
if st.session_state.history:
    st.header("🕒 GPA History")
    hist_df = pd.DataFrame(st.session_state.history)
    st.dataframe(hist_df, use_container_width=True)

    csv = hist_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download GPA History",
        csv,
        "gpa_history.csv",
        "text/csv"
    )