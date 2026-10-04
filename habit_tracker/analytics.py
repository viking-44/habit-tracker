from functools import reduce


def list_all_habits(habits: list) -> list:
    """Return all habits as a list (identity map over the collection)."""
    return list(map(lambda h: h, habits))


def filter_by_periodicity(habits: list, periodicity: str) -> list:
    """Return only habits whose periodicity matches the given value."""
    return list(filter(lambda h: h.periodicity == periodicity, habits))


def longest_streak_all(habits: list):
    """Return the habit with the highest longest_streak value, or None if empty.

    Uses reduce to fold over the list, keeping the habit with the greater streak.
    """
    if not habits:
        return None
    return reduce(
        lambda best, h: h if h.longest_streak() > best.longest_streak() else best,
        habits,
    )


def longest_streak_for(habit) -> int:
    """Return the longest streak ever recorded for a single habit."""
    return habit.longest_streak()
