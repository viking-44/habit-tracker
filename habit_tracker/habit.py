from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Habit:
    name: str
    periodicity: str  # 'daily' or 'weekly'
    creation_date: date
    completions: list = field(default_factory=list)
    id: Optional[int] = None

    def check_off(self, on: date = None) -> None:
        """Record a completion for the given date (defaults to today)."""
        on = on or date.today()
        if on not in self.completions:
            self.completions.append(on)

    def _completed_periods(self) -> set:
        """Return the set of period keys that have at least one completion."""
        if self.periodicity == 'daily':
            return {d.isoformat() for d in self.completions}
        return {f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}" for d in self.completions}

    def _period_key(self, d: date) -> str:
        if self.periodicity == 'daily':
            return d.isoformat()
        y, w, _ = d.isocalendar()
        return f"{y}-W{w:02d}"

    def _prev_period(self, d: date) -> date:
        if self.periodicity == 'daily':
            return d - timedelta(days=1)
        return d - timedelta(weeks=1)

    def _period_to_date(self, key: str) -> date:
        """Convert a period key back to the first day of that period."""
        if self.periodicity == 'daily':
            return date.fromisoformat(key)
        year, week = int(key[:4]), int(key[6:])
        return date.fromisocalendar(year, week, 1)

    def current_streak(self, as_of: date = None) -> int:
        """Count consecutive completed periods ending at as_of (or today).

        If the current period is not yet completed, we look back one period
        so an ongoing streak is not prematurely broken.
        """
        as_of = as_of or date.today()
        completed = self._completed_periods()
        d = as_of
        if self._period_key(d) not in completed:
            d = self._prev_period(d)
        streak = 0
        while self._period_key(d) in completed:
            streak += 1
            d = self._prev_period(d)
        return streak

    def longest_streak(self) -> int:
        """Return the longest consecutive run of completed periods ever recorded."""
        completed = self._completed_periods()
        if not completed:
            return 0
        periods = sorted(completed)
        max_streak = 1
        current = 1
        for i in range(1, len(periods)):
            prev_date = self._period_to_date(periods[i - 1])
            step = timedelta(days=1) if self.periodicity == 'daily' else timedelta(weeks=1)
            expected = self._period_key(prev_date + step)
            if periods[i] == expected:
                current += 1
                if current > max_streak:
                    max_streak = current
            else:
                current = 1
        return max_streak

    def is_broken(self, as_of: date = None) -> bool:
        """True if the habit was once active but the current streak is zero."""
        if not self.completions:
            return False
        return self.current_streak(as_of) == 0
