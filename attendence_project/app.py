import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date
import altair as alt

# ============================================================
# Advanced Attendance Management System
# Python + Streamlit + Pandas
# ============================================================

APP_DIR = Path(__file__).parent
STUDENTS_FILE = APP_DIR / "students.csv"
ATTENDANCE_FILE = APP_DIR / "attendance.csv"

st.set_page_config(
    page_title="Advanced Attendance System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# File / Data helper functions
# -----------------------------

def ensure_files():
    """Create persistent CSV files if they do not exist."""
    if not STUDENTS_FILE.exists():
        pd.DataFrame(columns=["student_id", "name"]).to_csv(
            STUDENTS_FILE, index=False
        )

    if not ATTENDANCE_FILE.exists():
        pd.DataFrame(
            columns=["date", "student_id", "name", "status"]
        ).to_csv(ATTENDANCE_FILE, index=False)


def load_students():
    ensure_files()
    df = pd.read_csv(STUDENTS_FILE, dtype=str)
    if df.empty:
        return pd.DataFrame(columns=["student_id", "name"])
    df["student_id"] = df["student_id"].astype(str)
    df["name"] = df["name"].astype(str)
    return df


def load_attendance():
    ensure_files()
    df = pd.read_csv(ATTENDANCE_FILE, dtype=str)
    if df.empty:
        return pd.DataFrame(columns=["date", "student_id", "name", "status"])
    df["date"] = df["date"].astype(str)
    df["student_id"] = df["student_id"].astype(str)
    df["name"] = df["name"].astype(str)
    df["status"] = df["status"].astype(str)
    return df


def save_students(df):
    df.to_csv(STUDENTS_FILE, index=False)


def save_attendance(df):
    df.to_csv(ATTENDANCE_FILE, index=False)


def next_student_id(students):
    """Generate the next numeric student ID."""
    if students.empty:
        return "1"

    numeric_ids = pd.to_numeric(students["student_id"], errors="coerce").dropna()
    if numeric_ids.empty:
        return str(len(students) + 1)

    return str(int(numeric_ids.max()) + 1)


def attendance_summary(students, attendance):
    """Build per-student attendance statistics."""
    if students.empty:
        return pd.DataFrame(
            columns=[
                "Student ID",
                "Student Name",
                "Total Days Marked",
                "Present",
                "Absent",
                "Attendance %",
            ]
        )

    rows = []

    for _, student in students.iterrows():
        sid = str(student["student_id"])
        name = student["name"]

        records = attendance[attendance["student_id"] == sid]
        total = len(records)
        present = int((records["status"] == "Present").sum())
        absent = int((records["status"] == "Absent").sum())
        percentage = (present / total * 100) if total else 0.0

        rows.append(
            {
                "Student ID": sid,
                "Student Name": name,
                "Total Days Marked": total,
                "Present": present,
                "Absent": absent,
                "Attendance %": percentage,
            }
        )

    return pd.DataFrame(rows)


def get_dates(attendance):
    if attendance.empty:
        return []
    return sorted(attendance["date"].dropna().unique(), reverse=True)


def clear_attendance():
    pd.DataFrame(
        columns=["date", "student_id", "name", "status"]
    ).to_csv(ATTENDANCE_FILE, index=False)


def clear_everything():
    pd.DataFrame(columns=["student_id", "name"]).to_csv(
        STUDENTS_FILE, index=False
    )
    clear_attendance()


# -----------------------------
# Initial data
# -----------------------------

ensure_files()

if "students" not in st.session_state:
    st.session_state.students = load_students()

if "attendance" not in st.session_state:
    st.session_state.attendance = load_attendance()

students = st.session_state.students
attendance = st.session_state.attendance

# -----------------------------
# Styling
# -----------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #777;
        margin-bottom: 1.2rem;
    }
    .low-attendance {
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Sidebar navigation
# -----------------------------

st.sidebar.title("📚 Attendance System")
st.sidebar.caption("Student attendance management")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "👨‍🎓 Students",
        "📝 Take Attendance",
        "📊 Reports",
        "⚙️ Settings",
    ],
)

st.sidebar.divider()
st.sidebar.info(
    "Data is stored locally in students.csv and attendance.csv "
    "so it remains available after restarting the app."
)

# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":
    st.markdown('<div class="main-title">📚 Attendance Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Overview of your class attendance.</div>',
        unsafe_allow_html=True,
    )

    summary = attendance_summary(students, attendance)

    total_students = len(students)
    total_days = attendance["date"].nunique() if not attendance.empty else 0
    total_present = int((attendance["status"] == "Present").sum())
    total_absent = int((attendance["status"] == "Absent").sum())

    total_marked = total_present + total_absent
    average_attendance = (
        total_present / total_marked * 100 if total_marked else 0
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👨‍🎓 Students", total_students)
    c2.metric("📅 Days Recorded", total_days)
    c3.metric("✅ Present", total_present)
    c4.metric("❌ Absent", total_absent)
    c5.metric("📊 Average", f"{average_attendance:.1f}%")

    st.divider()

    if students.empty:
        st.warning("No students have been added yet. Go to **Students** to create your class list.")
    else:
        st.subheader("📋 Attendance Summary")

        display = summary.copy()
        display["Attendance %"] = display["Attendance %"].map(
            lambda x: f"{x:.1f}%"
        )

        def highlight_low(row):
            try:
                value = float(str(row["Attendance %"]).replace("%", ""))
            except ValueError:
                value = 0
            return [
                "background-color: #ffdddd; color: #a00000; font-weight: bold"
                if value < 75
                else ""
                for _ in row
            ]

        st.dataframe(
            display.style.apply(highlight_low, axis=1),
            use_container_width=True,
            hide_index=True,
        )

        if not attendance.empty:
            st.subheader("📈 Attendance by Student")

            chart_data = summary[["Student Name", "Attendance %"]].copy()

            chart = (
                alt.Chart(chart_data)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "Student Name:N",
                        sort="-y",
                        title="Student",
                    ),
                    y=alt.Y(
                        "Attendance %:Q",
                        scale=alt.Scale(domain=[0, 100]),
                        title="Attendance %",
                    ),
                    tooltip=[
                        "Student Name",
                        alt.Tooltip(
                            "Attendance %:Q",
                            format=".1f",
                            title="Attendance %",
                        ),
                    ],
                )
                .properties(height=400)
            )

            st.altair_chart(chart, use_container_width=True)

# ============================================================
# STUDENTS
# ============================================================

elif page == "👨‍🎓 Students":
    st.title("👨‍🎓 Student Management")
    st.caption("Create and manage your class/student list.")

    with st.form("add_student_form", clear_on_submit=True):
        st.subheader("➕ Add Student")

        name = st.text_input(
            "Student name",
            placeholder="Example: John Doe",
        )

        submitted = st.form_submit_button(
            "Add Student",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            clean_name = name.strip()

            if not clean_name:
                st.error("Please enter a student name.")
            elif clean_name.lower() in students["name"].str.lower().tolist():
                st.warning("A student with this name already exists.")
            else:
                new_id = next_student_id(students)
                new_student = pd.DataFrame(
                    [{"student_id": new_id, "name": clean_name}]
                )

                students = pd.concat(
                    [students, new_student],
                    ignore_index=True,
                )

                save_students(students)
                st.session_state.students = students
                st.success(f"{clean_name} was added successfully.")
                st.rerun()

    st.divider()

    with st.expander("➕ Add Multiple Students"):
        st.write("Enter one student per line or separate names with commas.")

        bulk_text = st.text_area(
            "Student names",
            placeholder="Alice\nBob\nCharlie",
        )

        if st.button("Add All Students", type="primary"):
            raw_names = bulk_text.replace(",", "\n").splitlines()
            names = [x.strip() for x in raw_names if x.strip()]

            existing = set(students["name"].str.lower())
            added = []
            skipped = []

            for student_name in names:
                if student_name.lower() in existing:
                    skipped.append(student_name)
                    continue

                new_id = next_student_id(students)
                students = pd.concat(
                    [
                        students,
                        pd.DataFrame(
                            [{"student_id": new_id, "name": student_name}]
                        ),
                    ],
                    ignore_index=True,
                )

                existing.add(student_name.lower())
                added.append(student_name)

            save_students(students)
            st.session_state.students = students

            if added:
                st.success(f"Added {len(added)} student(s).")
            if skipped:
                st.warning(
                    "Skipped duplicate student(s): "
                    + ", ".join(skipped)
                )

            if added:
                st.rerun()

    st.divider()
    st.subheader(f"📋 Registered Students ({len(students)})")

    if students.empty:
        st.info("No students yet.")
    else:
        search = st.text_input(
            "🔎 Search students",
            placeholder="Search by name or ID",
        )

        filtered = students.copy()

        if search.strip():
            term = search.strip().lower()
            filtered = filtered[
                filtered["name"].str.lower().str.contains(term, na=False)
                | filtered["student_id"].str.lower().str.contains(term, na=False)
            ]

        st.dataframe(
            filtered.rename(
                columns={
                    "student_id": "Student ID",
                    "name": "Student Name",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("🗑️ Delete Student")

        delete_id = st.selectbox(
            "Select a student",
            options=students["student_id"].tolist(),
            format_func=lambda x: (
                f"{x} — "
                f"{students.loc[students['student_id'] == x, 'name'].iloc[0]}"
            ),
        )

        if st.button("Delete Selected Student", type="secondary"):
            selected_name = students.loc[
                students["student_id"] == delete_id, "name"
            ].iloc[0]

            students = students[
                students["student_id"] != delete_id
            ].copy()

            # Also remove that student's attendance records.
            attendance = attendance[
                attendance["student_id"] != delete_id
            ].copy()

            save_students(students)
            save_attendance(attendance)

            st.session_state.students = students
            st.session_state.attendance = attendance

            st.success(
                f"{selected_name} and their attendance records were deleted."
            )
            st.rerun()

# ============================================================
# TAKE ATTENDANCE
# ============================================================

elif page == "📝 Take Attendance":
    st.title("📝 Take Attendance")
    st.caption("Mark each student as present or absent.")

    if students.empty:
        st.warning("Please add students first.")
    else:
        selected_date = st.date_input(
            "📅 Attendance date",
            value=date.today(),
        )

        date_string = selected_date.isoformat()

        existing_for_date = attendance[
            attendance["date"] == date_string
        ].copy()

        st.write(
            f"**Date:** {selected_date.strftime('%A, %d %B %Y')}"
        )

        if not existing_for_date.empty:
            st.info(
                "Attendance already exists for this date. "
                "You can edit it and save again."
            )

        # Initialize checkbox state for this date.
        if "attendance_date" not in st.session_state:
            st.session_state.attendance_date = date_string

        if st.session_state.attendance_date != date_string:
            st.session_state.attendance_date = date_string

        # Determine existing status for each student.
        existing_status = {}
        for _, row in existing_for_date.iterrows():
            existing_status[str(row["student_id"])] = row["status"]

        col1, col2, col3 = st.columns(3)

        if col1.button("✅ Mark All Present", use_container_width=True):
            for _, student in students.iterrows():
                st.session_state[
                    f"present_{date_string}_{student['student_id']}"
                ] = True
            st.rerun()

        if col2.button("❌ Mark All Absent", use_container_width=True):
            for _, student in students.iterrows():
                st.session_state[
                    f"present_{date_string}_{student['student_id']}"
                ] = False
            st.rerun()

        if col3.button("↩️ Load Saved Attendance", use_container_width=True):
            for _, student in students.iterrows():
                sid = str(student["student_id"])
                key = f"present_{date_string}_{sid}"
                saved_value = existing_status.get(sid) == "Present"
                st.session_state[key] = saved_value
            st.rerun()

        st.divider()

        st.subheader("Students")

        with st.form("attendance_form"):
            for _, student in students.iterrows():
                sid = str(student["student_id"])
                key = f"present_{date_string}_{sid}"

                if key not in st.session_state:
                    st.session_state[key] = (
                        existing_status.get(sid) == "Present"
                    )

                st.checkbox(
                    f"{sid} — {student['name']}",
                    key=key,
                )

            save_button = st.form_submit_button(
                "💾 Save Attendance",
                type="primary",
                use_container_width=True,
            )

            if save_button:
                # Remove old records for this date.
                attendance = attendance[
                    attendance["date"] != date_string
                ].copy()

                new_records = []

                for _, student in students.iterrows():
                    sid = str(student["student_id"])
                    key = f"present_{date_string}_{sid}"

                    status = (
                        "Present"
                        if st.session_state.get(key, False)
                        else "Absent"
                    )

                    new_records.append(
                        {
                            "date": date_string,
                            "student_id": sid,
                            "name": student["name"],
                            "status": status,
                        }
                    )

                new_df = pd.DataFrame(new_records)

                attendance = pd.concat(
                    [attendance, new_df],
                    ignore_index=True,
                )

                attendance = attendance.sort_values(
                    ["date", "student_id"]
                ).reset_index(drop=True)

                save_attendance(attendance)
                st.session_state.attendance = attendance

                present_count = int(
                    (new_df["status"] == "Present").sum()
                )
                absent_count = len(new_df) - present_count

                st.success(
                    f"Attendance saved! Present: {present_count} | "
                    f"Absent: {absent_count}"
                )

# ============================================================
# REPORTS
# ============================================================

elif page == "📊 Reports":
    st.title("📊 Attendance Reports")

    summary = attendance_summary(students, attendance)

    if students.empty:
        st.info("Add students to generate reports.")
    else:
        st.subheader("👨‍🎓 Student Attendance Summary")

        min_percentage = st.slider(
            "Minimum attendance percentage",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
        )

        report = summary[
            summary["Attendance %"] >= min_percentage
        ].copy()

        report["Attendance %"] = report["Attendance %"].round(2)

        st.dataframe(
            report,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader("📅 Attendance History")

        if attendance.empty:
            st.info("No attendance records have been saved yet.")
        else:
            dates = get_dates(attendance)

            selected_report_date = st.selectbox(
                "Select a date",
                dates,
            )

            daily = attendance[
                attendance["date"] == selected_report_date
            ].copy()

            daily = daily.rename(
                columns={
                    "date": "Date",
                    "student_id": "Student ID",
                    "name": "Student Name",
                    "status": "Status",
                }
            )

            st.dataframe(
                daily,
                use_container_width=True,
                hide_index=True,
            )

            st.divider()
            st.subheader("📈 Attendance Trend")

            trend = (
                attendance.assign(
                    present=attendance["status"].eq("Present").astype(int)
                )
                .groupby("date", as_index=False)["present"]
                .mean()
            )

            trend["Attendance %"] = trend["present"] * 100

            trend_chart = (
                alt.Chart(trend)
                .mark_line(point=True)
                .encode(
                    x=alt.X("date:T", title="Date"),
                    y=alt.Y(
                        "Attendance %:Q",
                        scale=alt.Scale(domain=[0, 100]),
                        title="Attendance %",
                    ),
                    tooltip=[
                        "date:T",
                        alt.Tooltip(
                            "Attendance %:Q",
                            format=".1f",
                            title="Attendance %",
                        ),
                    ],
                )
                .properties(height=350)
            )

            st.altair_chart(
                trend_chart,
                use_container_width=True,
            )

        st.divider()
        st.subheader("⬇️ Export Reports")

        summary_csv = summary.to_csv(index=False).encode("utf-8")
        attendance_csv = attendance.to_csv(index=False).encode("utf-8")

        c1, c2 = st.columns(2)

        c1.download_button(
            "⬇️ Download Summary CSV",
            data=summary_csv,
            file_name="attendance_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )

        c2.download_button(
            "⬇️ Download Full Attendance CSV",
            data=attendance_csv,
            file_name="attendance_history.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ============================================================
# SETTINGS
# ============================================================

elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.caption("Manage stored attendance and application data.")

    st.subheader("📁 Current Data")

    c1, c2 = st.columns(2)
    c1.metric("Students", len(students))
    c2.metric("Attendance Records", len(attendance))

    st.divider()

    st.subheader("🧹 Clear Attendance")

    st.warning(
        "This removes all attendance records but keeps the student list."
    )

    if "confirm_clear_attendance" not in st.session_state:
        st.session_state.confirm_clear_attendance = False

    if st.button("Clear All Attendance", type="secondary"):
        st.session_state.confirm_clear_attendance = True

    if st.session_state.confirm_clear_attendance:
        st.error(
            "Are you sure? This action cannot be undone unless you have a backup."
        )

        c1, c2 = st.columns(2)

        if c1.button("Yes, Clear Attendance", type="primary"):
            clear_attendance()
            st.session_state.attendance = load_attendance()
            st.session_state.confirm_clear_attendance = False
            st.success("All attendance records have been cleared.")
            st.rerun()

        if c2.button("Cancel"):
            st.session_state.confirm_clear_attendance = False
            st.rerun()

    st.divider()

    st.subheader("⚠️ Reset Entire Application")

    st.warning(
        "This deletes ALL students and ALL attendance records."
    )

    if "confirm_reset" not in st.session_state:
        st.session_state.confirm_reset = False

    if st.button("Reset Everything", type="secondary"):
        st.session_state.confirm_reset = True

    if st.session_state.confirm_reset:
        st.error("This cannot be undone.")

        c1, c2 = st.columns(2)

        if c1.button("Yes, Reset Everything", type="primary"):
            clear_everything()

            st.session_state.students = load_students()
            st.session_state.attendance = load_attendance()
            st.session_state.confirm_reset = False

            st.success("Application data has been reset.")
            st.rerun()

        if c2.button("Cancel Reset"):
            st.session_state.confirm_reset = False
            st.rerun()

    st.divider()

    st.subheader("💾 Download Raw Data")

    students_csv = students.to_csv(index=False).encode("utf-8")
    attendance_csv = attendance.to_csv(index=False).encode("utf-8")

    c1, c2 = st.columns(2)

    c1.download_button(
        "Download Students CSV",
        students_csv,
        "students.csv",
        "text/csv",
        use_container_width=True,
    )

    c2.download_button(
        "Download Attendance CSV",
        attendance_csv,
        "attendance.csv",
        "text/csv",
        use_container_width=True,
    )

st.sidebar.divider()
st.sidebar.caption("Advanced Attendance System • Python + Streamlit + Pandas")
