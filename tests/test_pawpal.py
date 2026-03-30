import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, Schedule


def make_task(**kwargs):
    defaults = dict(
        name="Morning Walk",
        category="exercise",
        duration=30,
        priority="high",
        frequency="daily",
        preferred_time="morning",
        time="08:00",
        due_date=date.today(),
    )
    defaults.update(kwargs)
    return Task(**defaults)


def make_scheduler(*pets):
    owner = Owner(name="Alex", available_time=240)
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner)


# ── existing tests ────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", age=3)
    assert len(pet.tasks) == 0
    pet.tasks.append(make_task())
    assert len(pet.tasks) == 1


# ── sorting correctness ───────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """Tasks with different HH:MM times must come back earliest-first."""
    t1 = make_task(name="Evening Meds",  time="19:00", preferred_time="evening")
    t2 = make_task(name="Afternoon Walk", time="13:30", preferred_time="afternoon")
    t3 = make_task(name="Morning Feed",  time="07:00", preferred_time="morning")

    pet = Pet(name="Buddy", species="Dog", age=3, tasks=[t1, t2, t3])
    scheduler = make_scheduler(pet)

    sorted_tasks = scheduler.sort_by_time()

    assert [t.time for t in sorted_tasks] == ["07:00", "13:30", "19:00"]


# ── recurrence logic ──────────────────────────────────────────────────────────

def test_completing_daily_task_creates_next_occurrence():
    """Marking a daily task complete must append a new task due the following day."""
    today = date.today()
    task = make_task(name="Daily Walk", frequency="daily", due_date=today)
    pet = Pet(name="Buddy", species="Dog", age=3, tasks=[task])
    scheduler = make_scheduler(pet)

    next_task = scheduler.mark_task_complete(task)

    assert next_task is not None, "Expected a new Task for the next recurrence"
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert next_task in pet.tasks


def test_completing_non_recurring_task_returns_none():
    """A one-off (monthly) task must not generate a follow-up task."""
    task = make_task(name="Vet Visit", frequency="monthly")
    pet = Pet(name="Buddy", species="Dog", age=3, tasks=[task])
    scheduler = make_scheduler(pet)

    result = scheduler.mark_task_complete(task)

    assert result is None


# ── conflict detection ────────────────────────────────────────────────────────

def test_detect_time_conflicts_flags_duplicate_start_times():
    """Two tasks on different pets sharing an exact HH:MM time must produce a warning."""
    today = date.today()
    t1 = make_task(name="Walk Rex",   time="08:00", due_date=today)
    t2 = make_task(name="Feed Whiskers", time="08:00", due_date=today)

    dog = Pet(name="Rex",     species="Dog", age=2, tasks=[t1])
    cat = Pet(name="Whiskers", species="Cat", age=4, tasks=[t2])
    scheduler = make_scheduler(dog, cat)

    schedule = scheduler.generate_plan(reference_date=today)
    warnings = scheduler.detect_time_conflicts(schedule)

    assert len(warnings) >= 1
    assert any("08:00" in w for w in warnings)


def test_detect_time_conflicts_no_warning_when_times_differ():
    """Tasks at different times must not produce any conflict warnings."""
    today = date.today()
    t1 = make_task(name="Morning Walk", time="07:00", due_date=today)
    t2 = make_task(name="Evening Feed", time="18:00", due_date=today,
                   preferred_time="evening")

    pet = Pet(name="Buddy", species="Dog", age=3, tasks=[t1, t2])
    scheduler = make_scheduler(pet)

    schedule = scheduler.generate_plan(reference_date=today)
    warnings = scheduler.detect_time_conflicts(schedule)

    assert warnings == []
