import sqlite3
from datetime import date, timedelta
from habit_tracker.habit import Habit
from habit_tracker.db import init_db, save_habit, log_completion

# Anchor: 4-week window starts 2024-01-01 (Monday)
_START = date(2024, 1, 1)
_DAYS = [_START + timedelta(days=i) for i in range(28)]


def _day(offset: int) -> date:
    return _START + timedelta(days=offset)


# Completion schedules for the 5 predefined habits.
# Each entry is (name, periodicity, [offsets of completed days from _START])
_HABITS = [
    (
        "Morning Meditation",
        "daily",
        # Very consistent — only misses 3 days (offsets 6, 13, 20)
        [i for i in range(28) if i not in (6, 13, 20)],
    ),
    (
        "Read 30 Minutes",
        "daily",
        # Good habit, misses weekends and a couple of mid-week days
        [i for i in range(28) if i not in (5, 6, 12, 13, 19, 20)],
    ),
    (
        "Drink 8 Glasses of Water",
        "daily",
        # Inconsistent — completes roughly every other day
        [0, 2, 4, 5, 7, 9, 11, 14, 16, 18, 21, 23, 25, 27],
    ),
    (
        "Exercise",
        "weekly",
        # Completes in all 4 weeks — one completion per week (e.g. Wednesday)
        [2, 9, 16, 23],
    ),
    (
        "Weekly Review",
        "weekly",
        # Completes in weeks 1-3, misses week 4
        [6, 13, 20],
    ),
]


def seed(conn: sqlite3.Connection) -> None:
    """Populate the database with 5 predefined habits and 4 weeks of example data."""
    init_db(conn)
    for name, periodicity, offsets in _HABITS:
        habit_id = save_habit(
            conn,
            Habit(name=name, periodicity=periodicity, creation_date=_START),
        )
        for offset in offsets:
            log_completion(conn, habit_id, _day(offset))
