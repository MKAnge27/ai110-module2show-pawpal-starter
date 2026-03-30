import streamlit as st
from pawpal_system import Task, Pet, Owner, Schedule, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner & Pet Info")

col_o1, col_o2 = st.columns(2)
with col_o1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_time = st.number_input("Available time (minutes)", min_value=1, max_value=1440, value=90)
    preferences = st.text_input("Owner preferences (comma-separated)", value="")
with col_o2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_age = st.number_input("Pet age", min_value=0, max_value=30, value=0)
    special_needs = st.text_input("Special needs (comma-separated)", value="")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name=owner_name,
        available_time=int(available_time),
        preferences=[p.strip() for p in preferences.split(",") if p.strip()],
    )

if "pet" not in st.session_state:
    st.session_state.pet = Pet(
        name=pet_name,
        species=species,
        age=int(pet_age),
        special_needs=[s.strip() for s in special_needs.split(",") if s.strip()],
    )
    st.session_state.owner.add_pet(st.session_state.pet)

st.markdown("### Tasks")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    task_time = st.text_input("Start time (HH:MM)", value="08:00")

col5, col6, col7, col8 = st.columns(4)
with col5:
    category = st.text_input("Category", value="general")
with col6:
    frequency = st.selectbox("Frequency", ["daily", "every_other_day", "weekly", "biweekly", "monthly"])
with col7:
    preferred_time = st.selectbox("Preferred time", ["morning", "afternoon", "evening", "night"])
with col8:
    due_date = st.date_input("Due date")

if st.button("Add task"):
    task = Task(
        name=task_title,
        category=category,
        duration=int(duration),
        priority=priority,
        frequency=frequency,
        preferred_time=preferred_time,
        time=task_time,
        due_date=due_date,
    )
    st.session_state.pet.tasks.append(task)

current_tasks = st.session_state.pet.tasks
if current_tasks:
    scheduler_preview = Scheduler(st.session_state.owner)
    sorted_tasks = [t for t in scheduler_preview.sort_by_time() if t.is_due_today()]
    st.write("Current tasks (sorted by scheduled time):")
    st.dataframe([t.to_dict() for t in sorted_tasks], use_container_width=True)

    st.markdown("**Mark tasks complete:**")
    for task in sorted_tasks:
        label = f"{'~~' + task.name + '~~' if task.completed else task.name} ({task.time}, {task.duration} min)"
        if st.checkbox(label, value=task.completed, key=f"complete_{id(task)}"):
            if not task.completed:
                scheduler_preview.mark_task_complete(task)
                st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(st.session_state.owner)
    schedule = scheduler.generate_plan()

    # --- Time budget status ---
    used = schedule.total_duration
    available = st.session_state.owner.get_available_time()
    if schedule.is_within_time_budget():
        st.success(
            f"Schedule fits within your time budget: {used} / {available} min used."
        )
    else:
        st.warning(
            f"Schedule exceeds your time budget: {used} min used, only {available} min available."
        )

    # --- Scheduled tasks grouped by time slot ---
    if schedule.tasks:
        from collections import defaultdict
        from pawpal_system import TIME_SLOT_ORDER

        slots = defaultdict(list)
        for task in schedule.tasks:
            slots[task.preferred_time.lower()].append(task)

        st.markdown("#### Scheduled Tasks")
        for slot in sorted(slots, key=lambda s: TIME_SLOT_ORDER.get(s, 99)):
            st.markdown(f"**{slot.capitalize()}**")
            slot_rows = [
                {
                    "Task": t.name,
                    "Category": t.category,
                    "Duration (min)": t.duration,
                    "Priority": t.priority,
                    "Time": t.time,
                    "Status": "Done" if t.completed else "Pending",
                }
                for t in slots[slot]
            ]
            st.table(slot_rows)
    else:
        st.info("No tasks were scheduled. Try adding tasks above.")

    # --- Slot-budget conflict warnings ---
    conflicts = scheduler.detect_conflicts(schedule)
    for msg in conflicts:
        st.warning(msg.strip())

    # --- Exact start-time conflict warnings ---
    time_conflicts = scheduler.detect_time_conflicts(schedule)
    for msg in time_conflicts:
        st.warning(msg.strip())

    # --- Skipped / non-due tasks in an expander ---
    scheduled_ids = {id(t) for t in schedule.tasks}
    due_tasks = [t for t in scheduler.task_list if t.is_due_today(schedule.date)]
    skipped = [t for t in due_tasks if id(t) not in scheduled_ids]
    not_due = [t for t in scheduler.task_list if not t.is_due_today(schedule.date)]

    with st.expander("Plan details"):
        if skipped:
            st.markdown("**Tasks skipped (not enough time):**")
            st.table(
                [{"Task": t.name, "Duration (min)": t.duration} for t in skipped]
            )
        if not_due:
            st.markdown("**Tasks not due today (recurring):**")
            st.table(
                [{"Task": t.name, "Frequency": t.frequency} for t in not_due]
            )
        if not skipped and not not_due:
            st.success("All tasks were scheduled with no items skipped.")

    with st.expander("Plan explanation", expanded=True):
        st.text(scheduler.explain_plan(schedule))
