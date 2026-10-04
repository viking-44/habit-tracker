from datetime import date
from habit_tracker.habit import Habit


def _daily(*dates):
    h = Habit("Test", "daily", date(2024, 1, 1))
    h.completions = list(dates)
    return h


def _weekly(*dates):
    h = Habit("Test", "weekly", date(2024, 1, 1))
    h.completions = list(dates)
    return h


# --- check_off ---

def test_check_off_adds_date():
    h = _daily()
    h.check_off(date(2024, 1, 5))
    assert date(2024, 1, 5) in h.completions


def test_check_off_no_duplicate():
    h = _daily()
    h.check_off(date(2024, 1, 5))
    h.check_off(date(2024, 1, 5))
    assert h.completions.count(date(2024, 1, 5)) == 1


def test_check_off_defaults_to_today():
    h = _daily()
    h.check_off()
    assert date.today() in h.completions


# --- current_streak (daily) ---

def test_daily_streak_completed_today():
    today = date(2024, 1, 7)
    h = _daily(date(2024, 1, 5), date(2024, 1, 6), date(2024, 1, 7))
    assert h.current_streak(today) == 3


def test_daily_streak_not_completed_today_counts_yesterday():
    # Yesterday and day before completed; today not — streak stays at 2
    today = date(2024, 1, 7)
    h = _daily(date(2024, 1, 5), date(2024, 1, 6))
    assert h.current_streak(today) == 2


def test_daily_streak_zero_after_gap():
    today = date(2024, 1, 7)
    h = _daily(date(2024, 1, 1), date(2024, 1, 2))
    assert h.current_streak(today) == 0


def test_daily_streak_single_completion():
    today = date(2024, 1, 1)
    h = _daily(date(2024, 1, 1))
    assert h.current_streak(today) == 1


def test_daily_streak_empty():
    h = _daily()
    assert h.current_streak(date(2024, 1, 7)) == 0


# --- current_streak (weekly) ---

def test_weekly_streak_two_consecutive_weeks():
    # Week 1 and week 2 of 2024
    h = _weekly(date(2024, 1, 1), date(2024, 1, 8))
    assert h.current_streak(date(2024, 1, 8)) == 2


def test_weekly_streak_missing_current_week_counts_previous():
    # Week 1 completed, checking in week 2 before completing it
    h = _weekly(date(2024, 1, 1))
    assert h.current_streak(date(2024, 1, 8)) == 1


def test_weekly_streak_gap_breaks_streak():
    # Week 1 only; checking in week 3
    h = _weekly(date(2024, 1, 1))
    assert h.current_streak(date(2024, 1, 15)) == 0


# --- longest_streak ---

def test_daily_longest_streak_with_gap():
    h = _daily(
        date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3),
        date(2024, 1, 5), date(2024, 1, 6),
    )
    assert h.longest_streak() == 3


def test_daily_longest_streak_all_consecutive():
    h = _daily(date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3))
    assert h.longest_streak() == 3


def test_daily_longest_streak_no_completions():
    h = _daily()
    assert h.longest_streak() == 0


def test_weekly_longest_streak():
    h = _weekly(date(2024, 1, 1), date(2024, 1, 8), date(2024, 1, 22))
    # Week 1 + 2 consecutive, then gap, week 4 alone → longest = 2
    assert h.longest_streak() == 2


# --- is_broken ---

def test_is_broken_false_no_completions():
    h = _daily()
    assert h.is_broken(date(2024, 1, 7)) is False


def test_is_broken_false_active_streak():
    today = date(2024, 1, 7)
    h = _daily(date(2024, 1, 6), date(2024, 1, 7))
    assert h.is_broken(today) is False


def test_is_broken_true_after_gap():
    h = _daily(date(2024, 1, 1))
    assert h.is_broken(date(2024, 1, 7)) is True
