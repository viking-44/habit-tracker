# Habit Tracker

A command-line habit tracking application built with Python.  
Portfolio project for **DLBDSOOFPP01 — Object Oriented and Functional Programming with Python**  
IU Internationale Hochschule

---

## Requirements

- Python 3.7+
- Dependencies: `click`, `pytest` (see `requirements.txt`)

## Installation

```bash
# Clone or download the project, then enter the directory
cd DLBDSOOFPP01

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the application

All commands share a `--db` option that sets the database file path (defaults to `~/habits.db`).

```bash
# Load 5 predefined habits with 4 weeks of example data
python -m habit_tracker.cli seed

# Add a new habit
python -m habit_tracker.cli add "Morning Run" --periodicity daily
python -m habit_tracker.cli add "Weekly Review" --periodicity weekly

# Mark a habit as completed (defaults to today)
python -m habit_tracker.cli complete "Morning Run"

# Mark a habit as completed on a specific date
python -m habit_tracker.cli complete "Morning Run" --on 2024-03-15

# List all habits with current streak and status
python -m habit_tracker.cli list

# Filter the list by periodicity
python -m habit_tracker.cli list --periodicity daily

# Show analytics (streaks, longest streaks, broken habits)
python -m habit_tracker.cli analyse

# Analyse only weekly habits
python -m habit_tracker.cli analyse --periodicity weekly

# Delete a habit
python -m habit_tracker.cli delete "Morning Run"
```

## Running the tests

```bash
pytest tests/ -v
```

Expected output: **44 passed**.

---

## Project structure

```
DLBDSOOFPP01/
├── habit_tracker/
│   ├── __init__.py
│   ├── habit.py        # Habit class — domain model, no I/O
│   ├── db.py           # All SQLite3 operations
│   ├── analytics.py    # Pure functions (map / filter / reduce)
│   ├── fixtures.py     # 5 predefined habits + 4 weeks of data
│   └── cli.py          # Click CLI — the only user-facing layer
├── tests/
│   ├── __init__.py
│   ├── test_habit.py
│   ├── test_db.py
│   └── test_analytics.py
├── requirements.txt
└── README.md
```

### Design principles

- **`habit.py`** and **`analytics.py`** never import from `db.py` or `cli.py`. Data flows one way: CLI → db.py → Habit objects.
- **`analytics.py`** uses `map`, `filter`, and `reduce` exclusively — no loops.
- **SQLite3** (standard library) is used for persistence; no external database driver required.
- The CLI layer (`cli.py`) is fully decoupled from business logic, making it straightforward to replace with a GUI (Tkinter, web) without touching core modules.
