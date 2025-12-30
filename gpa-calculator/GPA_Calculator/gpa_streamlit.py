import streamlit as st
import pandas as pd

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="EduSphere",
    page_icon="🎓",
    layout="wide"
)

# =============================
# COURSES + WEIGHTS
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
    "GT / AP World History": None,
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
    return round(weight - ((100 - avg) * 0.1), 2)

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

    for course in hs_selected:
        st.subheader(course)

        if course == "GT / AP World History":
            year = st.radio("Which year?", [1, 2], horizontal=True)
            weight = 5.5 if year == 1 else 6.0
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
# GPA + ANALYTICS
# =============================
with tabs[2]:
    st.header("📊 GPA Results & Analytics")

    if st.button("🎯 Calculate GPA"):
        rows = []

        total_weighted = 0
        total_unweighted = 0
        count = 0

        # ----- Middle School Table -----
        for course, avg in ms_grades.items():
            rows.append({
                "School": "Middle",
                "Course": course,
                "Average": round(avg, 2),
                "Weight": "N/A",
                "GPA Impact": "N/A"
            })

        # ----- High School Table + GPA -----
        impacts = {}

        for course, (avg, weight) in hs_grades.items():
            gpa_val = weighted_gpa(avg, weight)
            impacts[course] = gpa_val

            rows.append({
                "School": "High",
                "Course": course,
                "Average": round(avg, 2),
                "Weight": weight,
                "GPA Impact": gpa_val
            })

            total_weighted += gpa_val
            total_unweighted += unweighted_gpa(avg)
            count += 1

        if count == 0:
            st.warning("No high school courses selected.")
            st.stop()

        final_weighted = round(total_weighted / count, 2)
        final_unweighted = round(total_unweighted / count, 2)

        st.success(f"🎓 **Weighted GPA:** {final_weighted}")
        st.success(f"📘 **Unweighted GPA:** {final_unweighted}")

        # =============================
        # ANALYTICS TABLE
        # =============================
        st.subheader("📋 Course GPA Breakdown")
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        # =============================
        # IMPACT ANALYSIS
        # =============================
        best = max(impacts, key=impacts.get)
        worst = min(impacts, key=impacts.get)

        st.subheader("📈 Impact Analysis")
        st.write(f"✅ **Helping your GPA the most:** {best} ({impacts[best]})")
        st.write(f"⚠️ **Bringing your GPA down the most:** {worst} ({impacts[worst]})")