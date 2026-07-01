# AeroBMI Health Tracker

A premium, high-fidelity desktop health tracker built using Python, Tkinter, and Matplotlib. AeroBMI offers a modern black dashboard interface for calculating, tracking, and plotting Body Mass Index (BMI) records with dynamic multi-user profile management.

---

## 🛠 Features & Advanced Checklist

The application fully implements the **Advanced Tier** requirements and incorporates custom features for an enhanced product experience:

*   **Premium Black UI Design System**: A dark interface configured with sleek borders, focus outlines, and responsive hover feedback.
*   **Multi-User & Profile Management**: Add, select, and delete profile records with automated input validation (e.g. name length, duplicate profile detection, and age/gender validation).
*   **Hybrid Measurement Engine**: Instant conversion switches between **Metric** (kg / cm) and **Imperial** (lb / in) inputs.
*   **Visual BMI Segment Gauge**: Custom Canvas-drawn graphical range slider indicating status index zones (Underweight, Normal, Overweight, Obese) with a precision slider point.
*   **Ideal Weight Calculator**: Dynamic estimation of normal weight limits ($BMI \in [18.5, 24.9]$) matching your active height and measurement unit.
*   **Unified History Logs**: An interactive grid display showing historical records across all profiles, supporting item deletions and CSV reload syncs.
*   **Matplotlib Trend Viz**: Interactive line charts of individual BMI fluctuations over time with colored health zone bands, dashed limit lines, and auto-scaling.
*   **Flat File CSV Storage**: Self-healing structure preserving database entries without requiring external server configurations.

---

## 📂 Architecture & Directory Structure

```
python/
│
├── venv/                 # Virtual environment (at parent root)
│
└── task 2/
    ├── main.py           # Entry-point bootstrapper
    ├── gui.py            # GUI view panels & styles
    ├── database.py       # CSV backend database logic
    ├── requirements.txt  # Dependencies list
    ├── README.md         # Documentation
    └── bmi_records.csv   # Stored logs database
```

---

## 💾 CSV Database Schema

AeroBMI implements structural record storage inside `bmi_records.csv`. Profile metadata blocks persist as placeholder rows (with empty weights, heights, BMIs, and timestamps) until a calculation record is written.

### Header Fields:
```csv
user_name,age,gender,weight_kg,height_m,bmi,recorded_at
```

*   `user_name` (String): Unique identifier representing the profile name.
*   `age` (Integer/Empty): User profile age (optional, bounds `[1, 120]`).
*   `gender` (String/Empty): Gender selection (`Male`, `Female`, `Unspecified`).
*   `weight_kg` (Float/Empty): Stored weight in kilograms.
*   `height_m` (Float/Empty): Stored height in meters.
*   `bmi` (Float/Empty): Calculated BMI value rounded to 2 decimal places.
*   `recorded_at` (Timestamp/Empty): Event registration timestamp (`YYYY-MM-DD HH:MM:SS`).

---

## 🚀 Setup & Execution

### Prerequisites:
*   Python 3.8 or higher.
*   Pip (Python Package Installer).

### Installation & Run:

1.  **Navigate** to the project directory:
    ```powershell
    cd "c:\Users\ADMIN\Desktop\lalit\python"
    ```

2.  **Activate** the Python Virtual Environment:
    ```powershell
    venv\Scripts\activate
    ```

3.  **Run the application** from the `task 2` directory:
    ```powershell
    cd "task 2"
    python main.py
    ```

---

## 📈 Visual Reference Guides

*   **Calculate Tab**: Input panel displaying active profile selectors, measurement unit toggles, and weight/height textboxes. Results show color-coded BMI readings, a visual gauge pointer, reference limits, ideal ranges, and recommendation texts.
*   **History Tab**: Displays all historical user logs in an interactive spreadsheet view, allowing selected record pruning.
*   **Trend Chart**: Renders a time-series plot of a selected user's health progress relative to normal diagnostic lines.
