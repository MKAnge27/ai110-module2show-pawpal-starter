from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import List


# Maps time-of-day labels to sort order for chronological scheduling
TIME_SLOT_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, "night": 3}

# Maps frequency strings to how many days between occurrences
FREQUENCY_INTERVALS = {
    "daily": 1,
    "every_other_day": 2,
    "weekly": 7,
    "biweekly": 14,
    "monthly": 30,
}

# Realistic available minutes per time slot for conflict detection
SLOT_BUDGETS = {"morning": 90, "afternoon": 60, "evening": 60, "night": 30}

# Sort order for task priority (used in generate_plan)
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    name: str
    category: str
    duration: int          # in minutes
    priority: str          # "high", "medium", "low"
    frequency: str         # "daily", "weekly", etc.
    preferred_time: str    # "morning", "afternoon", "evening"
    time: str = "00:00"    # specific time in "HH:MM" format for chronological sorting
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def is_schedulable(self, available_minutes: int) -> bool:
        """Return True if the task fits within the available time."""
        return self.duration <= available_minutes

    def is_due_today(self, reference_date: date = None) -> bool:
        """Return True if this task's due_date matches reference_date."""
        if reference_date is None:
            reference_date = date.today()
        return self.due_date == reference_date

    def to_dict(self) -> dict:
        """Return the task's fields as a dictionary."""
        return {
            "name": self.name,
            "category": self.category,
            "duration": self.duration,
            "priority": self.priority,
            "frequency": self.frequency,
            "preferred_time": self.preferred_time,
            "time": self.time,
            "due_date": self.due_date.isoformat(),
            "completed": self.completed,
        }


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def get_care_requirements(self) -> List[str]:
        """Return a list of task names representing this pet's care needs."""
        return [task.name for task in self.tasks]


class Owner:
    def __init__(self, name: str, available_time: int, preferences: List[str] = None):
        self.name = name
        self.available_time = available_time  # in minutes
        self.preferences = preferences if preferences is not None else []
        self.pets: List[Pet] = []

    def update_preferences(self, new_preferences: List[str]):
        """Replace the owner's scheduling preferences with a new list."""
        self.preferences = new_preferences

    def get_available_time(self) -> int:
        """Return the owner's total available time in minutes."""
        return self.available_time

    def add_pet(self, pet: Pet):
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of all tasks across every pet."""
        return [task for pet in self.pets for task in pet.tasks]


class Schedule:
    def __init__(self, date: date, owner: Owner):
        self.date = date
        self.owner = owner
        self.tasks: List[Task] = []
        self.total_duration: int = 0

    def add_task(self, task: Task):
        """Add a task to the schedule and update the total duration."""
        self.tasks.append(task)
        self.total_duration += task.duration

    def remove_task(self, task: Task):
        """Remove a task from the schedule and subtract its duration."""
        if task in self.tasks:
            self.tasks.remove(task)
            self.total_duration -= task.duration

    def is_within_time_budget(self) -> bool:
        """Return True if scheduled tasks fit within the owner's available time."""
        return self.total_duration <= self.owner.get_available_time()

    def filter_by_status(self, completed: bool) -> List["Task"]:
        """Return only tasks matching the given completion status."""
        return [t for t in self.tasks if t.completed == completed]

    def display(self) -> str:
        """Return a formatted string showing all scheduled tasks grouped by time slot."""
        lines = [
            f"Schedule for {self.owner.name} on {self.date}",
            f"Total time: {self.total_duration} min / {self.owner.get_available_time()} min available",
            "-" * 40,
        ]
        if not self.tasks:
            lines.append("No tasks scheduled.")
        else:
            # Group tasks by time slot in chronological order
            slots: dict = defaultdict(list)
            for task in self.tasks:
                slots[task.preferred_time.lower()].append(task)
            for slot in sorted(slots, key=lambda s: TIME_SLOT_ORDER.get(s, 99)):
                lines.append(f"\n  [{slot.upper()}]")
                for task in slots[slot]:
                    status = "done" if task.completed else "pending"
                    lines.append(
                        f"    {task.name} ({task.duration} min) "
                        f"— {task.priority} priority [{status}]"
                    )
        return "\n".join(lines)


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    @property
    def task_list(self) -> List[Task]:
        """Return all tasks from the owner's pets."""
        return self.owner.get_all_tasks()

    def mark_task_complete(self, task: Task) -> "Task | None":
        """Mark a task complete and, for daily/weekly tasks, create the next occurrence.

        Uses timedelta to calculate the next due date from the task's current due_date.
        The new Task is appended to whichever pet owns the completed task.
        Returns the newly created Task, or None for non-recurring frequencies.
        """
        task.mark_complete()

        recurring_frequencies = {"daily", "weekly"}
        if task.frequency.lower() not in recurring_frequencies:
            return None

        interval_days = FREQUENCY_INTERVALS[task.frequency.lower()]
        next_due = task.due_date + timedelta(days=interval_days)

        next_task = replace(task, due_date=next_due, completed=False)

        for pet in self.owner.pets:
            if task in pet.tasks:
                pet.tasks.append(next_task)
                break

        return next_task

    def sort_by_time(self) -> List[Task]:
        """Return all tasks sorted chronologically by their 'HH:MM' time attribute."""
        return sorted(self.task_list, key=lambda t: t.time)

    def filter_tasks(self, completed: bool = None, pet_name: str = None) -> List[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Pass `completed=True/False` to filter by status.
        Pass `pet_name` to restrict to one pet's tasks.
        Both filters can be combined.
        """
        results = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks belonging to the named pet (case-insensitive)."""
        return self.filter_tasks(pet_name=pet_name)

    def generate_plan(self, reference_date: date = None) -> Schedule:
        """Build a schedule sorted by priority then time-of-day, skipping non-due recurring tasks."""
        if reference_date is None:
            reference_date = date.today()

        schedule = Schedule(date=reference_date, owner=self.owner)

        # Only include tasks that are due today based on their recurrence interval
        due_tasks = [t for t in self.task_list if t.is_due_today(reference_date)]

        # Primary sort: priority (high → medium → low)
        # Secondary sort: time slot (morning → afternoon → evening)
        sorted_tasks = sorted(
            due_tasks,
            key=lambda t: (
                PRIORITY_ORDER.get(t.priority.lower(), 99),
                TIME_SLOT_ORDER.get(t.preferred_time.lower(), 99),
            ),
        )

        remaining_time = self.owner.get_available_time()
        for task in sorted_tasks:
            if task.is_schedulable(remaining_time):
                schedule.add_task(task)
                remaining_time -= task.duration

        return schedule

    def detect_conflicts(self, schedule: Schedule) -> List[str]:
        """Return warnings for time slots where scheduled duration exceeds the slot budget."""
        slot_totals: dict = defaultdict(int)
        slot_task_names: dict = defaultdict(list)

        for task in schedule.tasks:
            slot = task.preferred_time.lower()
            slot_totals[slot] += task.duration
            slot_task_names[slot].append(task.name)

        conflicts = []
        for slot, total in slot_totals.items():
            budget = SLOT_BUDGETS.get(slot, 60)
            if total > budget:
                conflicts.append(
                    f"  [!] {slot.capitalize()} slot overloaded: "
                    f"{total} min scheduled vs {budget} min budget "
                    f"({', '.join(slot_task_names[slot])})"
                )
        return conflicts

    def _pet_for(self, task: Task) -> str:
        """Return the name of the pet that owns the given task."""
        for pet in self.owner.pets:
            if task in pet.tasks:
                return pet.name
        return "unknown pet"

    def detect_time_conflicts(self, schedule: Schedule) -> List[str]:
        """Return warnings for any two tasks that share the exact same 'HH:MM' start time.

        Checks across all pets so cross-pet collisions are caught too.
        Returns warning strings rather than raising exceptions.
        """
        time_buckets: dict = defaultdict(list)
        for task in schedule.tasks:
            time_buckets[task.time].append(task)

        warnings = []
        for start_time, tasks in time_buckets.items():
            if len(tasks) < 2:
                continue
            labels = [f"'{t.name}' ({self._pet_for(t)})" for t in tasks]
            warnings.append(
                f"  [!] Time conflict at {start_time}: "
                + " and ".join(labels)
                + " are scheduled at the same time."
            )
        return warnings

    def explain_plan(self, schedule: Schedule) -> str:
        """Return a human-readable summary of the schedule including skipped tasks and conflicts."""
        pet_names = ", ".join(p.name for p in self.owner.pets)
        lines = [
            f"Plan for {self.owner.name} — pets: {pet_names}",
            f"Available time: {self.owner.get_available_time()} minutes",
            f"Tasks scheduled: {len(schedule.tasks)}",
            f"Total time used: {schedule.total_duration} minutes",
            "",
        ]

        if schedule.is_within_time_budget():
            lines.append("This plan fits within the available time budget.")
        else:
            lines.append("Warning: This plan exceeds the available time budget.")

        lines.append("")
        for task in schedule.tasks:
            lines.append(
                f"- {task.name}: {task.duration} min ({task.category}, "
                f"{task.frequency}, {task.preferred_time})"
            )

        # Single pass: split all tasks into due vs. not-due
        scheduled_ids = {id(t) for t in schedule.tasks}
        due, not_due = [], []
        for t in self.task_list:
            (due if t.is_due_today(schedule.date) else not_due).append(t)
        skipped = [t for t in due if id(t) not in scheduled_ids]

        if skipped:
            lines.append("")
            lines.append("Tasks not scheduled due to time constraints:")
            for task in skipped:
                lines.append(f"  * {task.name} ({task.duration} min)")

        if not_due:
            lines.append("")
            lines.append("Tasks not due today (recurring):")
            for task in not_due:
                lines.append(f"  ~ {task.name} (every {task.frequency})")

        # Slot-budget conflict report
        conflicts = self.detect_conflicts(schedule)
        if conflicts:
            lines.append("")
            lines.append("Slot budget warnings:")
            lines.extend(conflicts)

        # Exact start-time conflict report
        time_conflicts = self.detect_time_conflicts(schedule)
        if time_conflicts:
            lines.append("")
            lines.append("Time conflict warnings:")
            lines.extend(time_conflicts)

        return "\n".join(lines)
