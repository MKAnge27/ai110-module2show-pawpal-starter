from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler

# Create owner
owner = Owner(name="Alex", available_time=120, preferences=["morning", "evening"])

# Create pets
dog = Pet(name="Buddy", species="Dog", age=3, special_needs=["joint supplement"])
cat = Pet(name="Luna", species="Cat", age=5, special_needs=[])

# --- Buddy's tasks — added OUT OF ORDER intentionally ---
dog.tasks.append(Task(
    name="Joint Supplement",
    category="health",
    duration=5,
    priority="medium",
    frequency="daily",
    preferred_time="evening",
    time="18:30",
))
dog.tasks.append(Task(
    name="Bath Time",
    category="grooming",
    duration=45,
    priority="low",
    frequency="weekly",
    preferred_time="morning",
    time="10:00",
))
dog.tasks.append(Task(
    name="Feed Buddy",
    category="feeding",
    duration=10,
    priority="high",
    frequency="daily",
    preferred_time="morning",
    time="07:30",
))
dog.tasks.append(Task(
    name="Morning Walk",
    category="exercise",
    duration=30,
    priority="high",
    frequency="daily",
    preferred_time="morning",
    time="07:00",
))

# --- Luna's tasks — also added OUT OF ORDER ---
cat.tasks.append(Task(
    name="Litter Box Cleaning",
    category="hygiene",
    duration=10,
    priority="medium",
    frequency="every_other_day",
    preferred_time="morning",
    time="08:00",
))
cat.tasks.append(Task(
    name="Feed Luna",
    category="feeding",
    duration=5,
    priority="high",
    frequency="daily",
    preferred_time="evening",
    time="17:00",
))
cat.tasks.append(Task(
    name="Playtime with Luna",
    category="enrichment",
    duration=20,
    priority="medium",
    frequency="daily",
    preferred_time="afternoon",
    time="14:00",
))

# --- Deliberate time conflict: two tasks at the exact same time ---
# Buddy's "Evening Meds" and Luna's "Evening Brush" both at 18:00
dog.tasks.append(Task(
    name="Evening Meds",
    category="health",
    duration=5,
    priority="high",
    frequency="daily",
    preferred_time="evening",
    time="18:00",
))
cat.tasks.append(Task(
    name="Evening Brush",
    category="grooming",
    duration=10,
    priority="medium",
    frequency="daily",
    preferred_time="evening",
    time="18:00",       # same time as Evening Meds — triggers conflict warning
))

# Add pets to owner
owner.add_pet(dog)
owner.add_pet(cat)

# --- Generate and display the schedule ---
scheduler = Scheduler(owner)
schedule = scheduler.generate_plan()

print("=" * 40)
print("        TODAY'S SCHEDULE")
print("=" * 40)
print(schedule.display())
print()
print(scheduler.explain_plan(schedule))

# --- Demo: detect_time_conflicts ---
print()
print("=" * 40)
print("  TIME CONFLICT DETECTION")
print("=" * 40)
time_conflicts = scheduler.detect_time_conflicts(schedule)
if time_conflicts:
    for warning in time_conflicts:
        print(warning)
else:
    print("  No time conflicts detected.")

# --- Demo: sort_by_time ---
print()
print("=" * 40)
print("  ALL TASKS SORTED BY TIME (sort_by_time)")
print("=" * 40)
sorted_tasks = scheduler.sort_by_time()
for t in sorted_tasks:
    print(f"  {t.time}  {t.name} | {t.preferred_time} | {t.priority}")

# --- Demo: filter_tasks by pet name ---
print()
print("=" * 40)
print("  BUDDY'S TASKS (filter_tasks pet_name)")
print("=" * 40)
buddy_tasks = scheduler.filter_tasks(pet_name="Buddy")
for t in buddy_tasks:
    print(f"  {t.time}  {t.name} | {t.frequency} | {t.priority}")

# --- Demo: filter_tasks by completion status ---
print()
print("=" * 40)
print("  PENDING TASKS (filter_tasks completed=False)")
print("=" * 40)
pending = scheduler.filter_tasks(completed=False)
for t in pending:
    print(f"  {t.name} ({t.duration} min)")

# --- Demo: mark_task_complete with auto-recurrence ---
print()
print("=" * 40)
print("  MARK TASK COMPLETE + AUTO-RECURRENCE")
print("=" * 40)

# Complete "Morning Walk" (daily) — should auto-schedule for tomorrow
walk_task = next(t for t in schedule.tasks if t.name == "Morning Walk")
next_walk = scheduler.mark_task_complete(walk_task)
print(f"  Completed: '{walk_task.name}' (due {walk_task.due_date})")
if next_walk:
    print(f"  Next occurrence created: '{next_walk.name}' due {next_walk.due_date}")

# Complete "Bath Time" (weekly) — should auto-schedule 7 days out
# Bath Time defaults to today so it appears in today's schedule
bath_task = next((t for t in scheduler.task_list if t.name == "Bath Time"), None)
if bath_task:
    next_bath = scheduler.mark_task_complete(bath_task)
    print(f"  Completed: '{bath_task.name}' (due {bath_task.due_date})")
    if next_bath:
        print(f"  Next occurrence created: '{next_bath.name}' due {next_bath.due_date}")

# Verify next occurrences show up in tomorrow's plan
from datetime import timedelta
tomorrow = date.today() + timedelta(days=1)
print()
print(f"  --- Tomorrow's plan ({tomorrow}) ---")
tomorrow_schedule = scheduler.generate_plan(reference_date=tomorrow)
for t in tomorrow_schedule.tasks:
    print(f"  {t.time}  {t.name} | due {t.due_date}")

# --- Demo: combined filter — Luna's pending tasks ---
print()
print("=" * 40)
print("  LUNA'S PENDING TASKS (combined filter)")
print("=" * 40)
luna_pending = scheduler.filter_tasks(completed=False, pet_name="Luna")
for t in luna_pending:
    print(f"  {t.name} ({t.duration} min) | {t.time}")
