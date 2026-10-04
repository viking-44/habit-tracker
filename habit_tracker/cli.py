import sqlite3
from datetime import date
from pathlib import Path

import click

from habit_tracker.habit import Habit
from habit_tracker.db import (
    init_db,
    save_habit,
    log_completion,
    load_habits,
    delete_habit,
    get_habit_by_name,
)
from habit_tracker.analytics import (
    list_all_habits,
    filter_by_periodicity,
    longest_streak_all,
    longest_streak_for,
)
from habit_tracker.fixtures import seed as seed_fixtures

DEFAULT_DB = str(Path.home() / "habits.db")


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)
    return conn


@click.group()
@click.option("--db", default=DEFAULT_DB, show_default=True, help="Path to the SQLite database file.")
@click.pass_context
def cli(ctx, db):
    """Habit Tracker — build and analyse your daily and weekly habits."""
    ctx.ensure_object(dict)
    ctx.obj["conn"] = _connect(db)


@cli.command()
@click.argument("name")
@click.option(
    "--periodicity",
    "-p",
    type=click.Choice(["daily", "weekly"], case_sensitive=False),
    default="daily",
    show_default=True,
    help="How often the habit should be completed.",
)
@click.pass_context
def add(ctx, name, periodicity):
    """Add a new habit."""
    conn = ctx.obj["conn"]
    if get_habit_by_name(conn, name):
        click.echo(f"A habit named '{name}' already exists.")
        return
    habit = Habit(name=name, periodicity=periodicity, creation_date=date.today())
    save_habit(conn, habit)
    click.echo(f"Added '{name}' ({periodicity}).")


@cli.command()
@click.argument("name")
@click.option(
    "--on",
    default=None,
    help="Date to record the completion (YYYY-MM-DD). Defaults to today.",
)
@click.pass_context
def complete(ctx, name, on):
    """Mark a habit as completed (defaults to today)."""
    conn = ctx.obj["conn"]
    habit = get_habit_by_name(conn, name)
    if habit is None:
        click.echo(f"No habit named '{name}' found.")
        return
    completion_date = date.fromisoformat(on) if on else date.today()
    log_completion(conn, habit.id, completion_date)
    click.echo(f"Logged completion for '{name}' on {completion_date}.")


@cli.command("list")
@click.option(
    "--periodicity",
    "-p",
    type=click.Choice(["daily", "weekly"], case_sensitive=False),
    default=None,
    help="Filter by periodicity.",
)
@click.pass_context
def list_habits(ctx, periodicity):
    """List all habits with their current streak and status."""
    conn = ctx.obj["conn"]
    habits = load_habits(conn)
    if periodicity:
        habits = filter_by_periodicity(habits, periodicity)
    if not habits:
        click.echo("No habits found.")
        return
    click.echo(f"{'ID':<4} {'Name':<30} {'Period':<8} {'Streak':>6}  Status")
    click.echo("-" * 62)
    for h in list_all_habits(habits):
        streak = h.current_streak()
        status = "BROKEN" if h.is_broken() else ("active" if streak > 0 else "new")
        click.echo(f"{h.id:<4} {h.name:<30} {h.periodicity:<8} {streak:>6}  {status}")


@cli.command()
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this habit and all its data?")
@click.pass_context
def delete(ctx, name):
    """Delete a habit and all its recorded completions."""
    conn = ctx.obj["conn"]
    habit = get_habit_by_name(conn, name)
    if habit is None:
        click.echo(f"No habit named '{name}' found.")
        return
    delete_habit(conn, habit.id)
    click.echo(f"Deleted '{name}'.")


@cli.command()
@click.option(
    "--periodicity",
    "-p",
    type=click.Choice(["daily", "weekly"], case_sensitive=False),
    default=None,
    help="Restrict analysis to one periodicity.",
)
@click.pass_context
def analyse(ctx, periodicity):
    """Show analytics: streaks, best habit, and broken habits."""
    conn = ctx.obj["conn"]
    habits = load_habits(conn)
    if periodicity:
        habits = filter_by_periodicity(habits, periodicity)
    if not habits:
        click.echo("No habits to analyse.")
        return

    click.echo("\n=== Habit Analytics ===\n")
    click.echo(f"{'Name':<30} {'Period':<8} {'Cur.Streak':>10}  {'LongestStreak':>13}  Status")
    click.echo("-" * 72)
    for h in habits:
        streak = h.current_streak()
        longest = longest_streak_for(h)
        status = "BROKEN" if h.is_broken() else ("active" if streak > 0 else "new")
        click.echo(f"{h.name:<30} {h.periodicity:<8} {streak:>10}  {longest:>13}  {status}")

    best = longest_streak_all(habits)
    if best:
        click.echo(f"\nBest overall streak: '{best.name}' with {longest_streak_for(best)} consecutive period(s).")


@cli.command()
@click.pass_context
def seed(ctx):
    """Load 5 predefined habits with 4 weeks of example data (clears existing data)."""
    conn = ctx.obj["conn"]
    conn.execute("DELETE FROM completions")
    conn.execute("DELETE FROM habits")
    conn.commit()
    seed_fixtures(conn)
    click.echo("Seeded 5 habits with 28 days of example data.")


if __name__ == "__main__":
    cli()
