from dataclasses import dataclass, field
from datetime import date
from typing import List


class Owner:
    def __init__(self, name: str, available_time: int, preferences: List[str] = None):
        self.name = name
        self.available_time = available_time  # in minutes
        self.preferences = preferences if preferences is not None else []

    def update_preferences(self, new_preferences: List[str]):
        self.preferences = new_preferences

    def get_available_time(self) -> int:
        return self.available_time


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: List[str] = field(default_factory=list)

    def get_care_requirements(self) -> List[str]:
        requirements = []
        if self.species.lower() == "dog":
            requirements.extend(["daily walks", "feeding", "grooming"])
        elif self.species.lower() == "cat":
            requirements.extend(["feeding", "litter box cleaning", "playtime"])
        else:
            requirements.append("feeding")
        requirements.extend(self.special_needs)
        return requirements


@dataclass
class Task:
    name: str
    category: str
    duration: int  # in minutes
    priority: str  # e.g. "high", "medium", "low"
    frequency: str  # e.g. "daily", "weekly"
    preferred_time: str  # e.g. "morning", "afternoon", "evening"

    def is_schedulable(self, available_minutes: int) -> bool:
        return self.duration <= available_minutes

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "duration": self.duration,
            "priority": self.priority,
            "frequency": self.frequency,
            "preferred_time": self.preferred_time,
        }


class Schedule:
    def __init__(self, date: date, owner: Owner):
        self.date = date
        self.owner = owner
        self.tasks: List[Task] = []
        self.total_duration: int = 0

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.total_duration += task.duration

    def remove_task(self, task: Task):
        if task in self.tasks:
            self.tasks.remove(task)
            self.total_duration -= task.duration

    def is_within_time_budget(self) -> bool:
        return self.total_duration <= self.owner.get_available_time()

    def display(self) -> str:
        lines = [
            f"Schedule for {self.owner.name} on {self.date}",
            f"Total time: {self.total_duration} min / {self.owner.get_available_time()} min available",
            "-" * 40,
        ]
        if not self.tasks:
            lines.append("No tasks scheduled.")
        else:
            for task in self.tasks:
                lines.append(
                    f"[{task.preferred_time.capitalize()}] {task.name} "
                    f"({task.duration} min) — {task.priority} priority"
                )
        return "\n".join(lines)


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, task_list: List[Task] = None):
        self.owner = owner
        self.pet = pet
        self.task_list: List[Task] = task_list if task_list is not None else []

    def generate_plan(self) -> Schedule:
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
        lines = [
            f"Plan explanation for {self.owner.name}'s pet {self.pet.name}:",
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
