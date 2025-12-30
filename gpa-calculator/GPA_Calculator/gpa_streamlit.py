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
    page_title="GPA_Calculator",
    page_icon="📘",
    layout="centered"
)

# -----------------------------
# SIMPLE USER LOGIN / PROFILE
# -----------------------------
st.title("📘 GPA_Calculator")

username = st.text_input("Enter your username (use the same one every time):")
if not username:
    st.warning("Please enter your username to continue.")
    st.stop()

# User data storage
user_folder = "user_data"
if not os.path.exists(user_folder):
    os.makedirs(user_folder)

user_file = f"{user_folder}/{username}.json"
if os.path.exists(user_file):
    with open(user_file, "r") as f:
        user_data = json.load(f)
else:
    user_data = {"history": []}

st.success(f"Welcome, {username}!")

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
# COURSE SELECTION
# -----------------------------
st.header("📚 Courses & Grades")

selected = st.multiselect(
    "Select your courses",
    [f"{k}. {v[0]}" for k, v in courses.items()]
)

if not selected:
    st.warning("Please select at least one course.")
    st.stop()

# -----------------------------
# SEMESTER/QUARTER INPUT
# -----------------------------
quarters_done = st.slider("How many quarters completed this year?", 1, 4, 2)

grades = {}
gt_year = None

for item in selected:
    num = int(item.split(".")[0])
    name, base_weight = courses[num]
    st.subheader(name)

    # -----------------------------
    # Middle School input
    # -----------------------------
    if st.checkbox(f"Did you take {name} in Middle School?"):
        sem1 = st.number_input(f"{name} MS Semester 1 grade:", 0.0, 100.0, 90.0, key=f"{num}_ms1")
        sem2 = st.number_input(f"{name} MS Semester 2 grade:", 0.0, 100.0, 90.0, key=f"{num}_ms2")
        grades[name] = {"MS": [sem1, sem2]}

    # -----------------------------
    # GT Humanities year selection
    # -----------------------------
    if num == 9:
        gt_year = st.radio("GT Humanities year", [1, 2], horizontal=True)
        weight = 5.5 if gt_year == 1 else 6.0
    else:
        weight = base_weight

    # -----------------------------
    # High School input per quarter
    # -----------------------------
    qs = []
    for q in range(1, quarters_done + 1):
        qs.append(st.number_input(
            f"{name} HS Quarter {q} grade:",
            0.0, 100.0, 90.0,
            key=f"{num}_q{q}"
        ))
    grades[name] = grades.get(name, {})
    grades[name]['HS'] = qs
    grades[name]['weight'] = weight

# -----------------------------
# CALCULATE BUTTON
# -----------------------------
if st.button("📊 Calculate GPA", use_container_width=True):
    weighted_final_list = []
    unweighted_final_list = []
    df_data = {}

    for course_name, data in grades.items():
        # Middle School GPA
        if 'MS' in data:
            avg_ms = sum(data['MS'])/len(data['MS'])
            w_gpa_ms = weighted_gpa(avg_ms, data['weight'])
            uw_gpa_ms = unweighted_gpa(avg_ms)
            weighted_final_list.append(w_gpa_ms)
            unweighted_final_list.append(uw_gpa_ms)
            df_data[course_name + " MS"] = {"Weighted GPA": w_gpa_ms, "Unweighted GPA": uw_gpa_ms}
        # High School GPA
        if 'HS' in data:
            avg_hs = sum(data['HS'])/len(data['HS'])
            w_gpa_hs = weighted_gpa(avg_hs, data['weight'])
            uw_gpa_hs = unweighted_gpa(avg_hs)
            weighted_final_list.append(w_gpa_hs)
            unweighted_final_list.append(uw_gpa_hs)
            df_data[course_name + " HS"] = {"Weighted GPA": w_gpa_hs, "Unweighted GPA": uw_gpa_hs}

    # Final GPAs
    weighted_final = round(sum(weighted_final_list)/len(weighted_final_list), 2)
    unweighted_final = round(sum(unweighted_final_list)/len(unweighted_final_list), 2)

    st.success(f"🎯 **Weighted GPA:** {weighted_final}")
    st.success(f"📘 **Unweighted GPA:** {unweighted_final}")

    # -----------------------------
    # GPA Chart
    # -----------------------------
    df = pd.DataFrame(df_data).T
    st.subheader("📈 GPA Breakdown")
    st.bar_chart(df[["Weighted GPA", "Unweighted GPA"]])

    # -----------------------------
    # SAVE HISTORY
    # -----------------------------
    user_data["history"].append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Weighted GPA": weighted_final,
        "Unweighted GPA": unweighted_final,
        "grades": grades
    })

    with open(user_file, "w") as f:
        json.dump(user_data, f)

# -----------------------------
# HISTORY + DOWNLOAD
# -----------------------------
if user_data["history"]:
    st.header("🕒 GPA History")
    hist_df = pd.DataFrame(user_data["history"])
    st.dataframe(hist_df, use_container_width=True)

    csv = hist_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download GPA History",
        csv,
        "gpa_history.csv",
        "text/csv"
    )

# -----------------------------
# INSTALL AS APP TIP
# -----------------------------
st.info(
    "📱 **Install this as an app:**\n"
    "• iPhone: Safari → Share → Add to Home Screen\n"
    "• Android: Chrome → Add to Home Screen"
)