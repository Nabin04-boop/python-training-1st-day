# 📚 Advanced Attendance Management System

A complete student attendance management web app built with:

- Python
- Streamlit
- Pandas
- Altair

## Features

- Add students individually or in bulk
- Automatically assign student IDs
- Search students
- Delete students
- Select attendance date
- Present/Absent checkboxes
- Mark all Present / Absent
- Edit previously saved attendance
- Persistent CSV storage
- Attendance percentage calculations
- Low-attendance highlighting below 75%
- Dashboard metrics
- Attendance charts
- Student search and report filtering
- Date-based attendance history
- CSV exports
- Clear attendance data
- Full application reset with confirmation

## Folder structure

```text
advanced_attendance_system/
├── app.py
├── requirements.txt
├── README.md
├── students.csv       # created automatically
└── attendance.csv     # created automatically
```

## Installation

Open a terminal in this folder.

### 1. Create a virtual environment (recommended)

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

Streamlit will show a local URL. Open that URL in your browser.

## Data storage

The application automatically creates:

- `students.csv`
- `attendance.csv`

These files keep your data after restarting the application.

## Attendance formula

```text
Attendance % = (Present Days / Total Days Marked) × 100
```

Students below 75% are highlighted in the dashboard.

## Notes

Back up the CSV files before using the reset options if you have important data.
