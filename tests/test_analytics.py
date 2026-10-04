import sqlite3
from datetime import date
from habit_tracker.habit import Habit
from habit_tracker.db import load_habits
from habit_tracker.fixtures import seed
from habit_tracker.analytics import (
    list_all_habits,
    filter_by_periodicity,
    longest_streak_all,
    longest_streak_for,
)


# --- Helpers ---

def _habit(name, periodicity, *completions):
    h = Habit(name, periodicity, date(2024, 1, 1))
    h.completions = list(completions)
    return h


def fixture_habits():
    """Load the 5 predefined habits from an in-memory seeded database."""
    conn = sqlite3.connect(":memory:")
    seed(conn)
    return load_habits(conn)


# --- list_all_habits ---

def test_list_all_returns_all_habits():
    habits = fixture_habits()
    result = list_all_habits(habits)
    assert len(result) == 5


def test_list_all_empty():
    assert list_all_habits([]) == []


def test_list_all_returns_same_objects():
    habits = fixture_habits()
    result = list_all_habits(habits)
    assert result == habits


# --- filter_by_periodicity ---

def test_filter_daily_from_fixtures():
    habits = fixture_habits()
    daily = filter_by_periodicity(habits, "daily")
    assert len(daily) == 3
    assert all(h.periodicity == "daily" for h in daily)


def test_filter_weekly_from_fixtures():
    habits = fixture_habits()
    weekly = filter_by_periodicity(habits, "weekly")
    assert len(weekly) == 2
    assert all(h.periodicity == "weekly" for h in weekly)


def test_filter_no_match_returns_empty():
    habits = fixture_habits()
    result = filter_by_periodicity(habits, "monthly")
    assert result == []


# --- longest_streak_all ---

def test_longest_streak_all_returns_correct_habit():
    # Exercise habit completes all 4 weeks → longest streak 4 (highest among weekly habits)
    # Morning Meditation has 25/28 completions with long runs
    habits = fixture_habits()
    best = longest_streak_all(habits)
    assert best is not None
    # Morning Meditation should win: 7-day run (vs Exercise 4-week run)
    assert best.periodicity == "daily"


def test_longest_streak_all_empty():
    assert longest_streak_all([]) is None


def test_longest_streak_all_single_habit():
    h = _habit("Solo", "daily", date(2024, 1, 1), date(2024, 1, 2))
    assert longest_streak_all([h]) is h


def test_longest_streak_all_tie_returns_one():
    h1 = _habit("A", "daily", date(2024, 1, 1))
    h2 = _habit("B", "daily", date(2024, 1, 2))
    result = longest_streak_all([h1, h2])
    assert result in (h1, h2)


# --- longest_streak_for ---

def test_longest_streak_for_morning_meditation():
    habits = fixture_habits()
    meditation = next(h for h in habits if h.name == "Morning Meditation")
    assert longest_streak_for(meditation) == 7


def test_longest_streak_for_exercise():
    habits = fixture_habits()
    exercise = next(h for h in habits if h.name == "Exercise")
    assert longest_streak_for(exercise) == 4


def test_longest_streak_for_weekly_review():
    habits = fixture_habits()
    review = next(h for h in habits if h.name == "Weekly Review")
    assert longest_streak_for(review) == 3


def test_longest_streak_for_no_completions():
    h = _habit("Empty", "daily")
    assert longest_streak_for(h) == 0
