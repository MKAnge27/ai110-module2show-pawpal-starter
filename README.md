# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

### Run the test suite

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Test | Behavior verified |
|---|---|
| `test_mark_complete_changes_status` | Marking a task complete flips `completed` to `True` |
| `test_add_task_increases_pet_task_count` | Appending a task to a pet's list increments the count |
| `test_sort_by_time_returns_chronological_order` | `sort_by_time()` returns tasks ordered earliest HH:MM first |
| `test_completing_daily_task_creates_next_occurrence` | Completing a `daily` task appends a new task due the following day |
| `test_completing_non_recurring_task_returns_none` | Completing a non-recurring task (e.g. `monthly`) returns `None` — no phantom recurrence |
| `test_detect_time_conflicts_flags_duplicate_start_times` | Two tasks on different pets sharing the same start time produce a conflict warning |
| `test_detect_time_conflicts_no_warning_when_times_differ` | Tasks at distinct times produce zero false-positive warnings |

### Confidence Level: ★★★★☆ (4/5)

The core scheduling loop, chronological sorting, and time-conflict detection all behave correctly under both happy-path and edge-case conditions. One star is withheld because `mark_task_complete` silently skips rescheduling for `every_other_day`, `biweekly`, and `monthly` frequencies — those tasks stop recurring after the first completion despite being listed in `FREQUENCY_INTERVALS`. That gap is known and documented but not yet fixed.
