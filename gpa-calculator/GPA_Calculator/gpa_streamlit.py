import streamlit as st

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="EduSphere",
    page_icon="🎓",
    layout="wide"
)

# =============================
# COURSES + WEIGHTS (ONLY COURSES YOU MENTIONED)
# =============================
courses = {
    "Spanish 1": 5.0,
    "Spanish 2": 5.0,
    "Spanish 3": 5.5,
    "Spanish 4 AP": 6.0,
    "Algebra 1": 5.5,
    "Geometry": 5.5,
    "Algebra 2": 5.5,
    "AP Precalculus": 6.0,
    "GT / AP World History": None,  # year decides weight
    "Biology": 5.5,
    "Chemistry": 5.5,
    "AP Human Geography": 6.0,
    "Sports": 5.0,
    "Health": 5.0,
    "Computer Science": 5.5,
    "Instruments": 5.0
}

# =============================
# GPA HELPERS
# =============================
def weighted_gpa(avg, weight):
    return weight - ((100 - avg) * 0.1)

def unweighted_gpa(avg):
    if avg >= 90: return 4
    if avg >= 80: return 3
    if avg >= 70: return 2
    if avg >= 60: return 1
    return 0

# =============================
# UI
# =============================
st.title("🎓 EduSphere GPA Calculator")

tabs = st.tabs(["🏫 Middle School", "🎓 High School", "📊 GPA & Analytics"])

# =============================
# MIDDLE SCHOOL
# =============================
with tabs[0]:
    st.header("Middle School Courses")

    ms_selected = st.multiselect(
        "Select courses taken in middle school",
        list(courses.keys()),
        key="ms_courses"
    )

    ms_grades = {}

    for course in ms_selected:
        st.subheader(course)
        s1 = st.number_input(f"{course} – Semester 1", 0.0, 100.0, 90.0)
        s2 = st.number_input(f"{course} – Semester 2", 0.0, 100.0, 90.0)
        ms_grades[course] = (s1 + s2) / 2

# =============================
# HIGH SCHOOL
# =============================
with tabs[1]:
    st.header("High School Courses")

    hs_selected = st.multiselect(
        "Select courses taken in high school",
        list(courses.keys()),
        key="hs_courses"
    )

    quarters = st.slider("Quarters completed", 1, 4, 2)

    hs_grades = {}
    gt_year = None

    for course in hs_selected:
        st.subheader(course)

        if course == "GT / AP World History":
            gt_year = st.radio(
                "Which year?",
                [1, 2],
                horizontal=True
            )
            weight = 5.5 if gt_year == 1 else 6.0
        else:
            weight = courses[course]

        qs = []
        for q in range(1, quarters + 1):
            qs.append(
                st.number_input(
                    f"{course} – Quarter {q}",
                    0.0, 100.0, 90.0,
                    key=f"{course}_{q}"
                )
            )

        avg = sum(qs) / len(qs)
        hs_grades[course] = (avg, weight)

# =============================
# GPA + ANALYTICS (FIXED LOGIC)
# =============================
with tabs[2]:
    st.header("📊 GPA Results & Analytics")

    if st.button("🎯 Calculate GPA"):
        total_weighted_points = 0
        total_unweighted_points = 0
        class_count = 0

        for course, (avg, weight) in hs_grades.items():
            if weight is None:
                continue

            total_weighted_points += weighted_gpa(avg, weight)
            total_unweighted_points += unweighted_gpa(avg)
            class_count += 1

        if class_count == 0:
            st.warning("No high school courses selected.")
        else:
            final_weighted = round(total_weighted_points / class_count, 2)
            final_unweighted = round(total_unweighted_points / class_count, 2)

            st.success(f"🎓 **Weighted GPA:** {final_weighted}")
            st.success(f"📘 **Unweighted GPA:** {final_unweighted}")

            st.subheader("📈 GPA Analysis")

            if final_weighted >= 5.5:
                st.write("Your GPA is being boosted heavily by AP/GT courses.")
            elif final_weighted >= 5.0:
                st.write("Strong GPA — AP courses are helping, but performance matters most.")
            else:
                st.write("Lower performance in high-weight courses is pulling your GPA down.")