import sqlite3
from datetime import date
from habit_tracker.db import init_db, save_habit, log_completion, load_habits, delete_habit, get_habit_by_name
from habit_tracker.habit import Habit


def make_conn():
    """Return a fresh in-memory SQLite connection with the schema initialised."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)
    return conn


def make_habit(name="Morning Meditation", periodicity="daily"):
    return Habit(name=name, periodicity=periodicity, creation_date=date(2024, 1, 1))


# --- init_db ---

def test_init_db_creates_tables():
    conn = make_conn()
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "habits" in tables
    assert "completions" in tables


# --- save_habit ---

def test_save_habit_returns_id():
    conn = make_conn()
    habit_id = save_habit(conn, make_habit())
    assert isinstance(habit_id, int) and habit_id > 0


def test_save_habit_persists_fields():
    conn = make_conn()
    save_habit(conn, make_habit("Read 30 Minutes", "daily"))
    row = conn.execute("SELECT name, periodicity, creation_date FROM habits").fetchone()
    assert row == ("Read 30 Minutes", "daily", "2024-01-01")


def test_save_habit_duplicate_name_raises():
    conn = make_conn()
    save_habit(conn, make_habit())
    try:
        save_habit(conn, make_habit())
        assert False, "Expected IntegrityError"
    except sqlite3.IntegrityError:
        pass


# --- log_completion ---

def test_log_completion_persists():
    conn = make_conn()
    habit_id = save_habit(conn, make_habit())
    log_completion(conn, habit_id, date(2024, 1, 5))
    rows = conn.execute("SELECT completed_date FROM completions WHERE habit_id=?", (habit_id,)).fetchall()
    assert rows == [("2024-01-05",)]


def test_log_completion_ignores_duplicate():
    conn = make_conn()
    habit_id = save_habit(conn, make_habit())
    log_completion(conn, habit_id, date(2024, 1, 5))
    log_completion(conn, habit_id, date(2024, 1, 5))
    count = conn.execute("SELECT COUNT(*) FROM completions WHERE habit_id=?", (habit_id,)).fetchone()[0]
    assert count == 1


# --- load_habits ---

def test_load_habits_round_trip():
    conn = make_conn()
    habit_id = save_habit(conn, make_habit())
    log_completion(conn, habit_id, date(2024, 1, 1))
    log_completion(conn, habit_id, date(2024, 1, 2))
    habits = load_habits(conn)
    assert len(habits) == 1
    h = habits[0]
    assert h.name == "Morning Meditation"
    assert h.periodicity == "daily"
    assert h.id == habit_id
    assert date(2024, 1, 1) in h.completions
    assert date(2024, 1, 2) in h.completions


def test_load_habits_empty():
    conn = make_conn()
    assert load_habits(conn) == []


def test_load_habits_multiple():
    conn = make_conn()
    save_habit(conn, make_habit("H1", "daily"))
    save_habit(conn, make_habit("H2", "weekly"))
    habits = load_habits(conn)
    assert len(habits) == 2
    names = {h.name for h in habits}
    assert names == {"H1", "H2"}


# --- delete_habit ---

def test_delete_habit_removes_habit_and_completions():
    conn = make_conn()
    conn.execute("PRAGMA foreign_keys = ON")
    habit_id = save_habit(conn, make_habit())
    log_completion(conn, habit_id, date(2024, 1, 1))
    delete_habit(conn, habit_id)
    assert load_habits(conn) == []
    count = conn.execute("SELECT COUNT(*) FROM completions").fetchone()[0]
    assert count == 0


# --- get_habit_by_name ---

def test_get_habit_by_name_found():
    conn = make_conn()
    save_habit(conn, make_habit("Meditation"))
    h = get_habit_by_name(conn, "Meditation")
    assert h is not None
    assert h.name == "Meditation"


def test_get_habit_by_name_not_found():
    conn = make_conn()
    assert get_habit_by_name(conn, "Nonexistent") is None
