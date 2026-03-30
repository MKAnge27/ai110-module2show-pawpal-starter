from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class Task:
    name: str
    category: str
    duration: int          # in minutes
    priority: str          # "high", "medium", "low"
    frequency: str         # "daily", "weekly", etc.
    preferred_time: str    # "morning", "afternoon", "evening"
    completed: bool = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def is_schedulable(self, available_minutes: int) -> bool:
        """Return True if the task fits within the available time."""
        return self.duration <= available_minutes

    def to_dict(self) -> dict:
        """Return the task's fields as a dictionary."""
        return {
            "name": self.name,
            "category": self.category,
            "duration": self.duration,
            "priority": self.priority,
            "frequency": self.frequency,
            "preferred_time": self.preferred_time,
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
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


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

    def display(self) -> str:
        """Return a formatted string showing all scheduled tasks for the day."""
        lines = [
            f"Schedule for {self.owner.name} on {self.date}",
            f"Total time: {self.total_duration} min / {self.owner.get_available_time()} min available",
            "-" * 40,
        ]
        if not self.tasks:
            lines.append("No tasks scheduled.")
        else:
            for task in self.tasks:
                status = "done" if task.completed else "pending"
                lines.append(
                    f"[{task.preferred_time.capitalize()}] {task.name} "
                    f"({task.duration} min) — {task.priority} priority [{status}]"
                )
        return "\n".join(lines)


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    @property
    def task_list(self) -> List[Task]:
        """Return all tasks from the owner's pets."""
        return self.owner.get_all_tasks()

    def generate_plan(self) -> Schedule:
        """Build a priority-sorted schedule that fits within the owner's available time."""
        schedule = Schedule(date=date.today(), owner=self.owner)

        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_tasks = sorted(
            self.task_list,
            key=lambda t: priority_order.get(t.priority.lower(), 99),
        )

        remaining_time = self.owner.get_available_time()
        for task in sorted_tasks:
            if task.is_schedulable(remaining_time):
                schedule.add_task(task)
                remaining_time -= task.duration

        return schedule

    def explain_plan(self, schedule: Schedule) -> str:
        """Return a human-readable summary of the schedule including skipped tasks."""
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

        skipped = [t for t in self.task_list if t not in schedule.tasks]
        if skipped:
            lines.append("")
            lines.append("Tasks not scheduled due to time constraints:")
            for task in skipped:
                lines.append(f"  * {task.name} ({task.duration} min)")

        return "\n".join(lines)
