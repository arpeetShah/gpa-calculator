import streamlit as st
import pandas as pd
import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="GPA Calculator",
    page_icon="📘",
    layout="centered"
)

st.title("📘 GPA Calculator")
student_name = st.text_input("Your Name (optional)")

# -----------------------------
# COURSES AND WEIGHTS
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
    9: ("GT Humanities / AP World", None),  # Weight depends on year
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
# SESSION STATE
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

grades = {}
gt_year = None

# -----------------------------
# MIDDLE SCHOOL INPUT
# -----------------------------
st.header("🏫 Middle School Courses")
ms_courses_selected = st.multiselect(
    "Select your middle school courses:",
    [f"{k}. {v[0]}" for k, v in courses.items()]
)

for item in ms_courses_selected:
    num = int(item.split(".")[0])
    name, base_weight = courses[num]

    if num == 9:  # GT Humanities weight depends on year
        gt_year = st.radio(f"GT Humanities year for {name}?", [1, 2], horizontal=True)
        weight = 5.5 if gt_year == 1 else 6.0
    else:
        weight = base_weight

    st.subheader(name)
    sem1 = st.number_input(f"{name} Semester 1 grade", 0.0, 100.0, 90.0, key=f"MS_{num}_1")
    sem2 = st.number_input(f"{name} Semester 2 grade", 0.0, 100.0, 90.0, key=f"MS_{num}_2")

    avg = (sem1 + sem2) / 2
    grades[name] = {
        "Average": avg,
        "Weighted GPA": weighted_gpa(avg, weight),
        "Unweighted GPA": unweighted_gpa(avg)
    }

# -----------------------------
# HIGH SCHOOL INPUT
# -----------------------------
st.header("🎓 High School Courses")
hs_courses_selected = st.multiselect(
    "Select your high school courses:",
    [f"{k}. {v[0]}" for k, v in courses.items()]
)

if hs_courses_selected:
    quarters_done = st.slider("How many quarters completed?", 1, 4, 2)

    for item in hs_courses_selected:
        num = int(item.split(".")[0])
        name, base_weight = courses[num]

        if num == 9 and gt_year is None:  # Ask GT year if not already selected
            gt_year = st.radio(f"GT Humanities year for {name}?", [1, 2], horizontal=True)

        weight = 5.5 if (num == 9 and gt_year == 1) else (6.0 if num == 9 else base_weight)

        st.subheader(name)
        qs = []
        for q in range(1, quarters_done + 1):
            grade = st.number_input(f"{name} Quarter {q} grade", 0.0, 100.0, 90.0, key=f"HS_{num}_{q}")
            qs.append(grade)

        avg = sum(qs) / len(qs)
        grades[name] = {
            "Average": avg,
            "Weighted GPA": weighted_gpa(avg, weight),
            "Unweighted GPA": unweighted_gpa(avg)
        }

# -----------------------------
# CALCULATE GPA
# -----------------------------
if st.button("📊 Calculate GPA"):
    if not grades:
        st.warning("Please select at least one course.")
    else:
        df = pd.DataFrame(grades).T

        weighted_final = round(df["Weighted GPA"].mean(), 2)
        unweighted_final = round(df["Unweighted GPA"].mean(), 2)

        st.success(f"🎯 **Weighted GPA:** {weighted_final}")
        st.success(f"📘 **Unweighted GPA:** {unweighted_final}")

        # Bar chart
        st.subheader("📈 GPA Breakdown")
        st.bar_chart(df[["Weighted GPA", "Unweighted GPA"]])

        # Save history
        record = {
            "Name": student_name or "Anonymous",
            "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Weighted GPA": weighted_final,
            "Unweighted GPA": unweighted_final
        }
        st.session_state.history.append(record)

# -----------------------------
# HISTORY AND DOWNLOAD
# -----------------------------
if st.session_state.history:
    st.header("🕒 GPA History")
    hist_df = pd.DataFrame(st.session_state.history)
    st.dataframe(hist_df, use_container_width=True)

    csv = hist_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download GPA History", csv, "gpa_history.csv", "text/csv")

# -----------------------------
# INSTALL AS APP TIP
# -----------------------------
st.info(
    "📱 **Install this as an app:**\n"
    "• iPhone: Safari → Share → Add to Home Screen\n"
    "• Android: Chrome → Add to Home Screen"
)