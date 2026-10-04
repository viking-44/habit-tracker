import sqlite3
from datetime import date
from habit_tracker.habit import Habit


def init_db(conn: sqlite3.Connection) -> None:
    """Create the habits and completions tables if they do not already exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS habits (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT    NOT NULL UNIQUE,
            periodicity     TEXT    NOT NULL CHECK(periodicity IN ('daily', 'weekly')),
            creation_date   TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS completions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id        INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
            completed_date  TEXT    NOT NULL,
            UNIQUE(habit_id, completed_date)
        );
    """)
    conn.commit()


def save_habit(conn: sqlite3.Connection, habit: Habit) -> int:
    """Insert a new habit and return its assigned id."""
    cur = conn.execute(
        "INSERT INTO habits (name, periodicity, creation_date) VALUES (?, ?, ?)",
        (habit.name, habit.periodicity, habit.creation_date.isoformat()),
    )
    conn.commit()
    return cur.lastrowid


def log_completion(conn: sqlite3.Connection, habit_id: int, on: date) -> None:
    """Record a single completion for a habit; silently ignores duplicates."""
    conn.execute(
        "INSERT OR IGNORE INTO completions (habit_id, completed_date) VALUES (?, ?)",
        (habit_id, on.isoformat()),
    )
    conn.commit()


def load_habits(conn: sqlite3.Connection) -> list:
    """Load all habits and their completions from the database."""
    habits = []
    for row in conn.execute("SELECT id, name, periodicity, creation_date FROM habits ORDER BY id"):
        habit_id, name, periodicity, creation_date = row
        completions = [
            date.fromisoformat(r[0])
            for r in conn.execute(
                "SELECT completed_date FROM completions WHERE habit_id = ? ORDER BY completed_date",
                (habit_id,),
            )
        ]
        h = Habit(
            name=name,
            periodicity=periodicity,
            creation_date=date.fromisoformat(creation_date),
            completions=completions,
            id=habit_id,
        )
        habits.append(h)
    return habits


def delete_habit(conn: sqlite3.Connection, habit_id: int) -> None:
    """Delete a habit and all its completions (cascade)."""
    conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()


def get_habit_by_name(conn: sqlite3.Connection, name: str):
    """Return the Habit with the given name, or None if not found."""
    row = conn.execute(
        "SELECT id FROM habits WHERE name = ?", (name,)
    ).fetchone()
    if row is None:
        return None
    all_habits = load_habits(conn)
    return next((h for h in all_habits if h.id == row[0]), None)
