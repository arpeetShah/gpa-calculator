import streamlit as st
import pandas as pd

st.set_page_config(page_title="GPA Calculator", layout="centered")

st.title("GPA Calculator")

# -----------------------------
# COURSE LIST
# -----------------------------
courses = {
    "Spanish 1": 5.0,
    "Spanish 2": 5.0,
    "Spanish 3": 5.5,
    "Spanish 4 AP": 6.0,
    "Algebra 1": 5.5,
    "Geometry": 5.5,
    "Algebra 2": 5.5,
    "AP Precalculus": 6.0,
    "Biology": 5.5,
    "Chemistry": 5.5,
    "AP World History": 6.0,
    "AP Human Geography": 6.0,
    "Computer Science": 5.5,
    "AP Computer Science Principles": 6.0,
    "Health": 5.0,
    "Instruments": 5.0,
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
st.header("Select Courses Taken")

selected_courses = {}
for course in courses:
    selected_courses[course] = st.checkbox(course)

# -----------------------------
# MIDDLE SCHOOL
# -----------------------------
st.header("Middle School Grades (2 Semesters)")

ms_grades = {}
for course, checked in selected_courses.items():
    if checked:
        sem1 = st.number_input(
            f"{course} - Semester 1",
            0, 100, 90,
            key=f"ms_{course}_1"
        )
        sem2 = st.number_input(
            f"{course} - Semester 2",
            0, 100, 90,
            key=f"ms_{course}_2"
        )
        ms_grades[course] = (sem1 + sem2) / 2

# -----------------------------
# HIGH SCHOOL
# -----------------------------
st.header("High School Grades")

quarters_done = st.slider("Quarters completed", 1, 4, 2)

hs_grades = {}
for course, checked in selected_courses.items():
    if checked:
        qs = []
        for q in range(1, quarters_done + 1):
            qs.append(
                st.number_input(
                    f"{course} - Quarter {q}",
                    0, 100, 90,
                    key=f"hs_{course}_{q}"
                )
            )
        hs_grades[course] = sum(qs) / len(qs)

# -----------------------------
# CALCULATE BUTTON
# -----------------------------
if st.button("Calculate GPA"):
    records = []

    for course, checked in selected_courses.items():
        if checked:
            weight = courses[course]

            if course in ms_grades:
                avg = ms_grades[course]
                records.append({
                    "Course": course,
                    "Level": "Middle School",
                    "Weighted GPA": weighted_gpa(avg, weight),
                    "Unweighted GPA": unweighted_gpa(avg)
                })

            if course in hs_grades:
                avg = hs_grades[course]
                records.append({
                    "Course": course,
                    "Level": "High School",
                    "Weighted GPA": weighted_gpa(avg, weight),
                    "Unweighted GPA": unweighted_gpa(avg)
                })

    if not records:
        st.warning("No courses selected.")
    else:
        df = pd.DataFrame(records)

        weighted_final = round(df["Weighted GPA"].mean(), 2)
        unweighted_final = round(df["Unweighted GPA"].mean(), 2)

        st.success(f"Weighted GPA: {weighted_final}")
        st.success(f"Unweighted GPA: {unweighted_final}")

        st.subheader("GPA Analysis")
        if weighted_final >= 5.5:
            st.write("Your GPA is very strong due to high-weight courses.")
        elif weighted_final >= 4.5:
            st.write("Your GPA is solid but could improve with stronger performance in weighted classes.")
        else:
            st.write("Your GPA is being lowered by course averages; focus on improving GPA-heavy courses.")

        st.subheader("Breakdown")
        st.dataframe(df)