weighted = []
unweighted = []

for course, weight in courses.items():

    # check if course is taken (either MS or HS checkbox)
    c.execute("""
    SELECT taken FROM grades
    WHERE username=? AND course=? AND taken=1
    """, (st.session_state.user, course))

    if not c.fetchone():
        continue  # course not checked → skip entirely

    # ---------- HIGH SCHOOL ----------
    c.execute("""
    SELECT p1, p2, p3, p4 FROM grades
    WHERE username=? AND course=? AND section="HS"
    """, (st.session_state.user, course))
    hs = c.fetchone()

    if hs:
        hs_grades = [g for g in hs if g is not None]
        if hs_grades:
            avg = sum(hs_grades) / len(hs_grades)
            weighted.append(weighted_gpa(avg, weight))
            unweighted.append(unweighted_gpa(avg))
            continue  # HS takes priority

    # ---------- MIDDLE SCHOOL ----------
    c.execute("""
    SELECT p1, p2 FROM grades
    WHERE username=? AND course=? AND section="MS"
    """, (st.session_state.user, course))
    ms = c.fetchone()

    if ms:
        ms_grades = [g for g in ms if g is not None]
        if ms_grades:
            avg = sum(ms_grades) / len(ms_grades)
            weighted.append(weighted_gpa(avg, weight))
            unweighted.append(unweighted_gpa(avg))