import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date
import altair as alt

# ============================================================
# Advanced Attendance Management System
# Python + Streamlit + Pandas
#
# Features:
# - Student management
# - Daily attendance
# - Present/Absent marking
# - Attendance reports
# - Attendance percentage
# - Manual Present/Absent adjustments
# - CSV export
# - Persistent local data
# ============================================================

APP_DIR = Path(__file__).parent

STUDENTS_FILE = APP_DIR / "students.csv"
ATTENDANCE_FILE = APP_DIR / "attendance.csv"
ADJUSTMENTS_FILE = APP_DIR / "attendance_adjustments.csv"

st.set_page_config(
    page_title="Advanced Attendance System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# FILE / DATA HELPER FUNCTIONS
# ============================================================

def ensure_files():
    """Create persistent CSV files if they do not exist."""

    if not STUDENTS_FILE.exists():
        pd.DataFrame(
            columns=["student_id", "name"]
        ).to_csv(STUDENTS_FILE, index=False)

    if not ATTENDANCE_FILE.exists():
        pd.DataFrame(
            columns=["date", "student_id", "name", "status"]
        ).to_csv(ATTENDANCE_FILE, index=False)

    if not ADJUSTMENTS_FILE.exists():
        pd.DataFrame(
            columns=[
                "student_id",
                "present_adjustment",
                "absent_adjustment",
            ]
        ).to_csv(ADJUSTMENTS_FILE, index=False)


def load_students():
    ensure_files()

    df = pd.read_csv(
        STUDENTS_FILE,
        dtype=str,
    )

    if df.empty:
        return pd.DataFrame(
            columns=["student_id", "name"]
        )

    df["student_id"] = df["student_id"].astype(str)
    df["name"] = df["name"].astype(str)

    return df


def load_attendance():
    ensure_files()

    df = pd.read_csv(
        ATTENDANCE_FILE,
        dtype=str,
    )

    if df.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "student_id",
                "name",
                "status",
            ]
        )

    df["date"] = df["date"].astype(str)
    df["student_id"] = df["student_id"].astype(str)
    df["name"] = df["name"].astype(str)
    df["status"] = df["status"].astype(str)

    return df


def load_adjustments():
    ensure_files()

    df = pd.read_csv(
        ADJUSTMENTS_FILE,
        dtype=str,
    )

    if df.empty:
        return pd.DataFrame(
            columns=[
                "student_id",
                "present_adjustment",
                "absent_adjustment",
            ]
        )

    df["student_id"] = df["student_id"].astype(str)

    df["present_adjustment"] = pd.to_numeric(
        df["present_adjustment"],
        errors="coerce",
    ).fillna(0).astype(int)

    df["absent_adjustment"] = pd.to_numeric(
        df["absent_adjustment"],
        errors="coerce",
    ).fillna(0).astype(int)

    return df


def save_students(df):
    df.to_csv(
        STUDENTS_FILE,
        index=False,
    )


def save_attendance(df):
    df.to_csv(
        ATTENDANCE_FILE,
        index=False,
    )


def save_adjustments(df):
    df.to_csv(
        ADJUSTMENTS_FILE,
        index=False,
    )


def next_student_id(students):
    """Generate the next numeric student ID."""

    if students.empty:
        return "1"

    numeric_ids = pd.to_numeric(
        students["student_id"],
        errors="coerce",
    ).dropna()

    if numeric_ids.empty:
        return str(len(students) + 1)

    return str(
        int(numeric_ids.max()) + 1
    )


# ============================================================
# ATTENDANCE SUMMARY
# ============================================================

def attendance_summary(
    students,
    attendance,
    adjustments,
):
    """
    Build attendance statistics.

    Actual attendance comes from attendance.csv.

    Manual adjustments are added on top of the actual values.
    """

    if students.empty:
        return pd.DataFrame(
            columns=[
                "Student ID",
                "Student Name",
                "Total Days Marked",
                "Present",
                "Absent",
                "Present Adjustment",
                "Absent Adjustment",
                "Adjusted Total",
                "Attendance %",
            ]
        )

    rows = []

    for _, student in students.iterrows():

        sid = str(student["student_id"])
        name = student["name"]

        records = attendance[
            attendance["student_id"] == sid
        ]

        actual_total = len(records)

        actual_present = int(
            (records["status"] == "Present").sum()
        )

        actual_absent = int(
            (records["status"] == "Absent").sum()
        )

        adjustment_row = adjustments[
            adjustments["student_id"] == sid
        ]

        if adjustment_row.empty:
            present_adjustment = 0
            absent_adjustment = 0
        else:
            present_adjustment = int(
                adjustment_row.iloc[0][
                    "present_adjustment"
                ]
            )

            absent_adjustment = int(
                adjustment_row.iloc[0][
                    "absent_adjustment"
                ]
            )

        # Prevent adjusted values from becoming negative.
        adjusted_present = max(
            0,
            actual_present + present_adjustment,
        )

        adjusted_absent = max(
            0,
            actual_absent + absent_adjustment,
        )

        adjusted_total = (
            adjusted_present +
            adjusted_absent
        )

        percentage = (
            adjusted_present /
            adjusted_total *
            100
            if adjusted_total
            else 0.0
        )

        rows.append(
            {
                "Student ID": sid,
                "Student Name": name,
                "Total Days Marked": actual_total,
                "Present": adjusted_present,
                "Absent": adjusted_absent,
                "Present Adjustment": present_adjustment,
                "Absent Adjustment": absent_adjustment,
                "Adjusted Total": adjusted_total,
                "Attendance %": percentage,
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# DATE HELPERS
# ============================================================

def get_dates(attendance):

    if attendance.empty:
        return []

    return sorted(
        attendance["date"]
        .dropna()
        .unique(),
        reverse=True,
    )


# ============================================================
# CLEAR DATA FUNCTIONS
# ============================================================

def clear_attendance():

    pd.DataFrame(
        columns=[
            "date",
            "student_id",
            "name",
            "status",
        ]
    ).to_csv(
        ATTENDANCE_FILE,
        index=False,
    )


def clear_adjustments():

    pd.DataFrame(
        columns=[
            "student_id",
            "present_adjustment",
            "absent_adjustment",
        ]
    ).to_csv(
        ADJUSTMENTS_FILE,
        index=False,
    )


def clear_everything():

    pd.DataFrame(
        columns=[
            "student_id",
            "name",
        ]
    ).to_csv(
        STUDENTS_FILE,
        index=False,
    )

    clear_attendance()
    clear_adjustments()


# ============================================================
# UPDATE ATTENDANCE ADJUSTMENT
# ============================================================

def change_adjustment(
    student_id,
    adjustment_type,
    amount,
):
    """
    Increase or decrease Present/Absent adjustment.
    """

    adjustments = st.session_state.adjustments.copy()

    student_id = str(student_id)

    if student_id not in adjustments[
        "student_id"
    ].astype(str).values:

        new_row = pd.DataFrame(
            [
                {
                    "student_id": student_id,
                    "present_adjustment": 0,
                    "absent_adjustment": 0,
                }
            ]
        )

        adjustments = pd.concat(
            [
                adjustments,
                new_row,
            ],
            ignore_index=True,
        )

    mask = (
        adjustments["student_id"].astype(str)
        == student_id
    )

    if adjustment_type == "present":

        current = int(
            adjustments.loc[
                mask,
                "present_adjustment",
            ].iloc[0]
        )

        adjustments.loc[
            mask,
            "present_adjustment",
        ] = current + amount

    elif adjustment_type == "absent":

        current = int(
            adjustments.loc[
                mask,
                "absent_adjustment",
            ].iloc[0]
        )

        adjustments.loc[
            mask,
            "absent_adjustment",
        ] = current + amount

    save_adjustments(adjustments)

    st.session_state.adjustments = adjustments


# ============================================================
# INITIAL DATA
# ============================================================

ensure_files()

if "students" not in st.session_state:
    st.session_state.students = load_students()

if "attendance" not in st.session_state:
    st.session_state.attendance = load_attendance()

if "adjustments" not in st.session_state:
    st.session_state.adjustments = load_adjustments()


students = st.session_state.students
attendance = st.session_state.attendance
adjustments = st.session_state.adjustments


# ============================================================
# STYLING
# ============================================================

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

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "📚 Attendance System"
)

st.sidebar.caption(
    "Student attendance management"
)

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
    "Data is stored locally in students.csv, "
    "attendance.csv and attendance_adjustments.csv."
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="main-title">'
        '📚 Attendance Dashboard'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        'Overview of your class attendance.'
        '</div>',
        unsafe_allow_html=True,
    )

    summary = attendance_summary(
        students,
        attendance,
        adjustments,
    )

    total_students = len(students)

    total_days = (
        attendance["date"].nunique()
        if not attendance.empty
        else 0
    )

    total_present = int(
        (attendance["status"] == "Present").sum()
    )

    total_absent = int(
        (attendance["status"] == "Absent").sum()
    )

    total_marked = (
        total_present +
        total_absent
    )

    average_attendance = (
        total_present /
        total_marked *
        100
        if total_marked
        else 0
    )

    # Apply manual adjustments to dashboard average.
    if not summary.empty:
        average_attendance = summary[
            "Attendance %"
        ].mean()

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "👨‍🎓 Students",
        total_students,
    )

    c2.metric(
        "📅 Days Recorded",
        total_days,
    )

    c3.metric(
        "✅ Present",
        int(summary["Present"].sum())
        if not summary.empty
        else total_present,
    )

    c4.metric(
        "❌ Absent",
        int(summary["Absent"].sum())
        if not summary.empty
        else total_absent,
    )

    c5.metric(
        "📊 Average",
        f"{average_attendance:.1f}%",
    )

    st.divider()

    if students.empty:

        st.warning(
            "No students have been added yet. "
            "Go to **Students** to create your class list."
        )

    else:

        st.subheader(
            "📋 Attendance Summary"
        )

        display = summary.copy()

        display["Attendance %"] = display[
            "Attendance %"
        ].map(
            lambda x: f"{x:.1f}%"
        )

        def highlight_low(row):

            try:
                value = float(
                    str(
                        row["Attendance %"]
                    ).replace("%", "")
                )

            except ValueError:
                value = 0

            return [
                (
                    "background-color: #ffdddd; "
                    "color: #a00000; "
                    "font-weight: bold"
                )
                if value < 75
                else ""
                for _ in row
            ]

        st.dataframe(
            display.style.apply(
                highlight_low,
                axis=1,
            ),
            use_container_width=True,
            hide_index=True,
        )

        if not attendance.empty:

            st.subheader(
                "📈 Attendance by Student"
            )

            chart_data = summary[
                [
                    "Student Name",
                    "Attendance %",
                ]
            ].copy()

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
                        scale=alt.Scale(
                            domain=[0, 100]
                        ),
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
                .properties(
                    height=400
                )
            )

            st.altair_chart(
                chart,
                use_container_width=True,
            )


# ============================================================
# STUDENTS
# ============================================================

elif page == "👨‍🎓 Students":

    st.title(
        "👨‍🎓 Student Management"
    )

    st.caption(
        "Create and manage your class/student list."
    )

    with st.form(
        "add_student_form",
        clear_on_submit=True,
    ):

        st.subheader(
            "➕ Add Student"
        )

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

                st.error(
                    "Please enter a student name."
                )

            elif (
                clean_name.lower()
                in students["name"]
                .str.lower()
                .tolist()
            ):

                st.warning(
                    "A student with this name already exists."
                )

            else:

                new_id = next_student_id(
                    students
                )

                new_student = pd.DataFrame(
                    [
                        {
                            "student_id": new_id,
                            "name": clean_name,
                        }
                    ]
                )

                students = pd.concat(
                    [
                        students,
                        new_student,
                    ],
                    ignore_index=True,
                )

                save_students(students)

                st.session_state.students = (
                    students
                )

                st.success(
                    f"{clean_name} was added successfully."
                )

                st.rerun()

    st.divider()

    with st.expander(
        "➕ Add Multiple Students"
    ):

        st.write(
            "Enter one student per line "
            "or separate names with commas."
        )

        bulk_text = st.text_area(
            "Student names",
            placeholder="Alice\nBob\nCharlie",
        )

        if st.button(
            "Add All Students",
            type="primary",
        ):

            raw_names = (
                bulk_text
                .replace(",", "\n")
                .splitlines()
            )

            names = [
                x.strip()
                for x in raw_names
                if x.strip()
            ]

            existing = set(
                students["name"]
                .str.lower()
            )

            added = []
            skipped = []

            for student_name in names:

                if (
                    student_name.lower()
                    in existing
                ):

                    skipped.append(
                        student_name
                    )

                    continue

                new_id = next_student_id(
                    students
                )

                students = pd.concat(
                    [
                        students,
                        pd.DataFrame(
                            [
                                {
                                    "student_id": new_id,
                                    "name": student_name,
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )

                existing.add(
                    student_name.lower()
                )

                added.append(
                    student_name
                )

            save_students(students)

            st.session_state.students = (
                students
            )

            if added:

                st.success(
                    f"Added {len(added)} student(s)."
                )

            if skipped:

                st.warning(
                    "Skipped duplicate student(s): "
                    + ", ".join(skipped)
                )

            if added:
                st.rerun()

    st.divider()

    st.subheader(
        f"📋 Registered Students ({len(students)})"
    )

    if students.empty:

        st.info(
            "No students yet."
        )

    else:

        search = st.text_input(
            "🔎 Search students",
            placeholder="Search by name or ID",
        )

        filtered = students.copy()

        if search.strip():

            term = search.strip().lower()

            filtered = filtered[
                filtered["name"]
                .str.lower()
                .str.contains(
                    term,
                    na=False,
                )
                |
                filtered["student_id"]
                .str.lower()
                .str.contains(
                    term,
                    na=False,
                )
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

        st.subheader(
            "🗑️ Delete Student"
        )

        delete_id = st.selectbox(
            "Select a student",
            options=students[
                "student_id"
            ].tolist(),
            format_func=lambda x: (
                f"{x} — "
                f"{students.loc[students['student_id'] == x, 'name'].iloc[0]}"
            ),
        )

        if st.button(
            "Delete Selected Student",
            type="secondary",
        ):

            selected_name = students.loc[
                students["student_id"]
                == delete_id,
                "name",
            ].iloc[0]

            students = students[
                students["student_id"]
                != delete_id
            ].copy()

            attendance = attendance[
                attendance["student_id"]
                != delete_id
            ].copy()

            adjustments = adjustments[
                adjustments["student_id"]
                != delete_id
            ].copy()

            save_students(students)
            save_attendance(attendance)
            save_adjustments(adjustments)

            st.session_state.students = (
                students
            )

            st.session_state.attendance = (
                attendance
            )

            st.session_state.adjustments = (
                adjustments
            )

            st.success(
                f"{selected_name} and their attendance records were deleted."
            )

            st.rerun()


# ============================================================
# TAKE ATTENDANCE
# ============================================================

elif page == "📝 Take Attendance":

    st.title(
        "📝 Take Attendance"
    )

    st.caption(
        "Mark each student as present or absent."
    )

    if students.empty:

        st.warning(
            "Please add students first."
        )

    else:

        selected_date = st.date_input(
            "📅 Attendance date",
            value=date.today(),
        )

        date_string = (
            selected_date.isoformat()
        )

        existing_for_date = attendance[
            attendance["date"]
            == date_string
        ].copy()

        st.write(
            f"**Date:** "
            f"{selected_date.strftime('%A, %d %B %Y')}"
        )

        if not existing_for_date.empty:

            st.info(
                "Attendance already exists for this date. "
                "You can edit it and save again."
            )

        if (
            "attendance_date"
            not in st.session_state
        ):

            st.session_state.attendance_date = (
                date_string
            )

        if (
            st.session_state.attendance_date
            != date_string
        ):

            st.session_state.attendance_date = (
                date_string
            )

        existing_status = {}

        for _, row in existing_for_date.iterrows():

            existing_status[
                str(row["student_id"])
            ] = row["status"]

        col1, col2, col3 = st.columns(3)

        if col1.button(
            "✅ Mark All Present",
            use_container_width=True,
        ):

            for _, student in students.iterrows():

                st.session_state[
                    f"present_{date_string}_{student['student_id']}"
                ] = True

            st.rerun()

        if col2.button(
            "❌ Mark All Absent",
            use_container_width=True,
        ):

            for _, student in students.iterrows():

                st.session_state[
                    f"present_{date_string}_{student['student_id']}"
                ] = False

            st.rerun()

        if col3.button(
            "↩️ Load Saved Attendance",
            use_container_width=True,
        ):

            for _, student in students.iterrows():

                sid = str(
                    student["student_id"]
                )

                key = (
                    f"present_{date_string}_{sid}"
                )

                saved_value = (
                    existing_status.get(sid)
                    == "Present"
                )

                st.session_state[key] = (
                    saved_value
                )

            st.rerun()

        st.divider()

        st.subheader(
            "Students"
        )

        with st.form(
            "attendance_form"
        ):

            for _, student in students.iterrows():

                sid = str(
                    student["student_id"]
                )

                key = (
                    f"present_{date_string}_{sid}"
                )

                if key not in st.session_state:

                    st.session_state[key] = (
                        existing_status.get(sid)
                        == "Present"
                    )

                st.checkbox(
                    f"{sid} — {student['name']}",
                    key=key,
                )

            save_button = (
                st.form_submit_button(
                    "💾 Save Attendance",
                    type="primary",
                    use_container_width=True,
                )
            )

            if save_button:

                attendance = attendance[
                    attendance["date"]
                    != date_string
                ].copy()

                new_records = []

                for _, student in students.iterrows():

                    sid = str(
                        student["student_id"]
                    )

                    key = (
                        f"present_{date_string}_{sid}"
                    )

                    status = (
                        "Present"
                        if st.session_state.get(
                            key,
                            False,
                        )
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

                new_df = pd.DataFrame(
                    new_records
                )

                attendance = pd.concat(
                    [
                        attendance,
                        new_df,
                    ],
                    ignore_index=True,
                )

                attendance = (
                    attendance
                    .sort_values(
                        [
                            "date",
                            "student_id",
                        ]
                    )
                    .reset_index(
                        drop=True
                    )
                )

                save_attendance(
                    attendance
                )

                st.session_state.attendance = (
                    attendance
                )

                present_count = int(
                    (
                        new_df["status"]
                        == "Present"
                    ).sum()
                )

                absent_count = (
                    len(new_df)
                    - present_count
                )

                st.success(
                    f"Attendance saved! "
                    f"Present: {present_count} | "
                    f"Absent: {absent_count}"
                )


# ============================================================
# REPORTS
# ============================================================

elif page == "📊 Reports":

    st.title(
        "📊 Attendance Reports"
    )

    summary = attendance_summary(
        students,
        attendance,
        adjustments,
    )

    if students.empty:

        st.info(
            "Add students to generate reports."
        )

    else:

        st.subheader(
            "👨‍🎓 Student Attendance Summary"
        )

        st.info(
            "Use the buttons below to manually "
            "increase or decrease a student's "
            "Present or Absent count."
        )

        # ----------------------------------------------------
        # MANUAL PRESENT / ABSENT CONTROLS
        # ----------------------------------------------------

        for _, student in students.iterrows():

            sid = str(
                student["student_id"]
            )

            student_name = student["name"]

            student_summary = summary[
                summary["Student ID"] == sid
            ]

            if student_summary.empty:
                continue

            row = student_summary.iloc[0]

            current_present = int(
                row["Present"]
            )

            current_absent = int(
                row["Absent"]
            )

            current_percentage = float(
                row["Attendance %"]
            )

            st.markdown(
                f"### 👤 {sid} — {student_name}"
            )

            c1, c2, c3, c4, c5 = st.columns(5)

            c1.metric(
                "Attendance",
                f"{current_percentage:.1f}%",
            )

            c2.metric(
                "Present",
                current_present,
            )

            c3.metric(
                "Absent",
                current_absent,
            )

            if c4.button(
                "➕ Present",
                key=f"plus_present_{sid}",
                use_container_width=True,
            ):

                change_adjustment(
                    sid,
                    "present",
                    1,
                )

                st.rerun()

            if c5.button(
                "➖ Present",
                key=f"minus_present_{sid}",
                use_container_width=True,
            ):

                # Do not allow adjusted Present
                # count to become negative.
                actual_present = int(
                    (
                        attendance[
                            attendance[
                                "student_id"
                            ] == sid
                        ]["status"]
                        == "Present"
                    ).sum()
                )

                current_adjustment = 0

                existing_adjustment = (
                    adjustments[
                        adjustments[
                            "student_id"
                        ] == sid
                    ]
                )

                if not existing_adjustment.empty:

                    current_adjustment = int(
                        existing_adjustment.iloc[0][
                            "present_adjustment"
                        ]
                    )

                if (
                    actual_present
                    + current_adjustment
                    > 0
                ):

                    change_adjustment(
                        sid,
                        "present",
                        -1,
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Present count cannot go below 0."
                    )

            c6, c7 = st.columns(2)

            if c6.button(
                "➕ Absent",
                key=f"plus_absent_{sid}",
                use_container_width=True,
            ):

                change_adjustment(
                    sid,
                    "absent",
                    1,
                )

                st.rerun()

            if c7.button(
                "➖ Absent",
                key=f"minus_absent_{sid}",
                use_container_width=True,
            ):

                actual_absent = int(
                    (
                        attendance[
                            attendance[
                                "student_id"
                            ] == sid
                        ]["status"]
                        == "Absent"
                    ).sum()
                )

                current_adjustment = 0

                existing_adjustment = (
                    adjustments[
                        adjustments[
                            "student_id"
                        ] == sid
                    ]
                )

                if not existing_adjustment.empty:

                    current_adjustment = int(
                        existing_adjustment.iloc[0][
                            "absent_adjustment"
                        ]
                    )

                if (
                    actual_absent
                    + current_adjustment
                    > 0
                ):

                    change_adjustment(
                        sid,
                        "absent",
                        -1,
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Absent count cannot go below 0."
                    )

            st.divider()

        # ----------------------------------------------------
        # FILTER REPORT
        # ----------------------------------------------------

        st.subheader(
            "📋 Filtered Attendance Report"
        )

        min_percentage = st.slider(
            "Minimum attendance percentage",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
        )

        # Recalculate after any adjustments.
        summary = attendance_summary(
            students,
            attendance,
            adjustments,
        )

        report = summary[
            summary["Attendance %"]
            >= min_percentage
        ].copy()

        report["Attendance %"] = (
            report["Attendance %"]
            .round(2)
        )

        st.dataframe(
            report,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        # ----------------------------------------------------
        # ATTENDANCE HISTORY
        # ----------------------------------------------------

        st.subheader(
            "📅 Attendance History"
        )

        if attendance.empty:

            st.info(
                "No attendance records have been saved yet."
            )

        else:

            dates = get_dates(
                attendance
            )

            selected_report_date = (
                st.selectbox(
                    "Select a date",
                    dates,
                )
            )

            daily = attendance[
                attendance["date"]
                == selected_report_date
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

            # ------------------------------------------------
            # ATTENDANCE TREND
            # ------------------------------------------------

            st.subheader(
                "📈 Attendance Trend"
            )

            trend = (
                attendance.assign(
                    present=attendance[
                        "status"
                    ]
                    .eq("Present")
                    .astype(int)
                )
                .groupby(
                    "date",
                    as_index=False,
                )["present"]
                .mean()
            )

            trend["Attendance %"] = (
                trend["present"] * 100
            )

            trend_chart = (
                alt.Chart(trend)
                .mark_line(
                    point=True
                )
                .encode(
                    x=alt.X(
                        "date:T",
                        title="Date",
                    ),
                    y=alt.Y(
                        "Attendance %:Q",
                        scale=alt.Scale(
                            domain=[0, 100]
                        ),
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
                .properties(
                    height=350
                )
            )

            st.altair_chart(
                trend_chart,
                use_container_width=True,
            )

        st.divider()

        # ----------------------------------------------------
        # EXPORT
        # ----------------------------------------------------

        st.subheader(
            "⬇️ Export Reports"
        )

        summary_csv = (
            summary
            .to_csv(index=False)
            .encode("utf-8")
        )

        attendance_csv = (
            attendance
            .to_csv(index=False)
            .encode("utf-8")
        )

        adjustments_csv = (
            adjustments
            .to_csv(index=False)
            .encode("utf-8")
        )

        c1, c2, c3 = st.columns(3)

        c1.download_button(
            "⬇️ Download Summary CSV",
            data=summary_csv,
            file_name="attendance_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )

        c2.download_button(
            "⬇️ Download Attendance CSV",
            data=attendance_csv,
            file_name="attendance_history.csv",
            mime="text/csv",
            use_container_width=True,
        )

        c3.download_button(
            "⬇️ Download Adjustments CSV",
            data=adjustments_csv,
            file_name="attendance_adjustments.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ============================================================
# SETTINGS
# ============================================================

elif page == "⚙️ Settings":

    st.title(
        "⚙️ Settings"
    )

    st.caption(
        "Manage stored attendance and application data."
    )

    st.subheader(
        "📁 Current Data"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Students",
        len(students),
    )

    c2.metric(
        "Attendance Records",
        len(attendance),
    )

    c3.metric(
        "Manual Adjustments",
        len(adjustments),
    )

    st.divider()

    # --------------------------------------------------------
    # CLEAR ATTENDANCE
    # --------------------------------------------------------

    st.subheader(
        "🧹 Clear Attendance"
    )

    st.warning(
        "This removes all attendance records "
        "but keeps the student list and manual adjustments."
    )

    if (
        "confirm_clear_attendance"
        not in st.session_state
    ):

        st.session_state.confirm_clear_attendance = (
            False
        )

    if st.button(
        "Clear All Attendance",
        type="secondary",
    ):

        st.session_state.confirm_clear_attendance = (
            True
        )

    if st.session_state.confirm_clear_attendance:

        st.error(
            "Are you sure? This action cannot be undone "
            "unless you have a backup."
        )

        c1, c2 = st.columns(2)

        if c1.button(
            "Yes, Clear Attendance",
            type="primary",
        ):

            clear_attendance()

            st.session_state.attendance = (
                load_attendance()
            )

            st.session_state.confirm_clear_attendance = (
                False
            )

            st.success(
                "All attendance records have been cleared."
            )

            st.rerun()

        if c2.button(
            "Cancel"
        ):

            st.session_state.confirm_clear_attendance = (
                False
            )

            st.rerun()

    st.divider()

    # --------------------------------------------------------
    # CLEAR MANUAL ADJUSTMENTS
    # --------------------------------------------------------

    st.subheader(
        "🔄 Reset Manual Adjustments"
    )

    st.warning(
        "This sets all manually added Present/Absent "
        "adjustments back to zero."
    )

    if (
        "confirm_clear_adjustments"
        not in st.session_state
    ):

        st.session_state.confirm_clear_adjustments = (
            False
        )

    if st.button(
        "Reset All Adjustments",
        type="secondary",
    ):

        st.session_state.confirm_clear_adjustments = (
            True
        )

    if st.session_state.confirm_clear_adjustments:

        st.error(
            "Are you sure you want to reset all adjustments?"
        )

        c1, c2 = st.columns(2)

        if c1.button(
            "Yes, Reset Adjustments",
            type="primary",
        ):

            clear_adjustments()

            st.session_state.adjustments = (
                load_adjustments()
            )

            st.session_state.confirm_clear_adjustments = (
                False
            )

            st.success(
                "All manual attendance adjustments have been reset."
            )

            st.rerun()

        if c2.button(
            "Cancel",
        ):

            st.session_state.confirm_clear_adjustments = (
                False
            )

            st.rerun()

    st.divider()

    # --------------------------------------------------------
    # RESET EVERYTHING
    # --------------------------------------------------------

    st.subheader(
        "⚠️ Reset Entire Application"
    )

    st.warning(
        "This deletes ALL students, ALL attendance "
        "records and ALL manual adjustments."
    )

    if (
        "confirm_reset"
        not in st.session_state
    ):

        st.session_state.confirm_reset = (
            False
        )

    if st.button(
        "Reset Everything",
        type="secondary",
    ):

        st.session_state.confirm_reset = (
            True
        )

    if st.session_state.confirm_reset:

        st.error(
            "This cannot be undone."
        )

        c1, c2 = st.columns(2)

        if c1.button(
            "Yes, Reset Everything",
            type="primary",
        ):

            clear_everything()

            st.session_state.students = (
                load_students()
            )

            st.session_state.attendance = (
                load_attendance()
            )

            st.session_state.adjustments = (
                load_adjustments()
            )

            st.session_state.confirm_reset = (
                False
            )

            st.success(
                "Application data has been reset."
            )

            st.rerun()

        if c2.button(
            "Cancel Reset",
        ):

            st.session_state.confirm_reset = (
                False
            )

            st.rerun()

    st.divider()

    # --------------------------------------------------------
    # DOWNLOAD RAW DATA
    # --------------------------------------------------------

    st.subheader(
        "💾 Download Raw Data"
    )

    students_csv = (
        students
        .to_csv(index=False)
        .encode("utf-8")
    )

    attendance_csv = (
        attendance
        .to_csv(index=False)
        .encode("utf-8")
    )

    adjustments_csv = (
        adjustments
        .to_csv(index=False)
        .encode("utf-8")
    )

    c1, c2, c3 = st.columns(3)

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

    c3.download_button(
        "Download Adjustments CSV",
        adjustments_csv,
        "attendance_adjustments.csv",
        "text/csv",
        use_container_width=True,
    )


# ============================================================
# SIDEBAR FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "Advanced Attendance System • "
    "Python + Streamlit + Pandas"
)
