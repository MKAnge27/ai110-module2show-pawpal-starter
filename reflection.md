# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The app is built around three core user actions. First, the user adds pet care tasks, things like walks, feedings, or medication, each one with a name, duration, and priority. Second, the user sets what time they're available during the day while giving the owener info and pet info. Third, the user generates a daily plan, and the app schedules the tasks that fit within the time constraints, prioritized by importance and explaining its choices.

- What classes did you include, and what responsibilities did you assign to each? 
I used five classes. Owner holds the user's name, available time, and preferences. Pet holds the animal's basic info. Task represents one care activity with duration and priority. Schedule is the final daily plan. Scheduler takes all of that and figures out which tasks to include.

**b. Design changes**

- Did your design change during implementation? 
Yes the design changed during implementation, originally planned to store just the owner's name or available time inside Schedule, but changed it to store the full Owner object so the app could explain its decisions properly.
- If yes, describe at least one change and why you made it. 
Changed it to store the full Owner object so the app could explain its decisions properly.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
The scheduler considers time, task priority, and due dates. Recurring tasks that aren't due today get filtered out entirely before scheduling even starts.
- How did you decide which constraints mattered most?
Time is the hard limit, nothing goes over it. Priority decides what gets included first when there isn't room for everything.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The scheduler uses a greedy algorithm — it goes through tasks in priority order and adds each one if it fits in the remaining time. It doesn't try to find the best possible combination.
- Why is that tradeoff reasonable for this scenario?
It keeps the logic simple and predictable. The downside is that a small low-priority task that would have fit might get skipped just because a larger high-priority task already used up the remaining time, but for a daily pet care schedule that's an acceptable tradeoff.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)? AI was use to brainstorm the different and design the mermaid class diagram based on the attributes and methods. To review the relationship and ensure it made since. Also used to understand it output and reasoning and ask for feedback.
- What kinds of prompts or questions were most helpful?
What are certain methods, their functiions and why do they belong to a specific class. Why do a certain thing over another. I'm designing a pet care app with the four classes identified above. Create a Mermaid.js class diagram based on the brainstormed attributes and methods.


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  While examining the generated class diagram on mermaid site. Notice a part of the diagram that showed Pet uses the Scheduler instead of Scheduler uses pet, Pet should have no knownledge of Scheduler.
- How did you evaluate or verify what the AI suggested?
  Evaluated the suggestion by simply understanding the relationship between Pet and Scheduler. Identified which class uses or depends on the other, and confirming that the arrows in the diagram accurately represented that direction of use.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test? 
Tested that mark_complete() changes a task's status to done, and that adding a task to a pet actually increases its task count.
- Why were these tests important?
These are the two most basic things the app depends on. If either one silently breaks, everything built on top of them breaks too.
**b. Confidence**

- How confident are you that your scheduler works correctly? 
Pretty confident for current path. The tests confirm the building blocks work, and the schedule output looked correct when it ran. 
- What edge cases would you test next if you had more time?
There are still no tests yet for edge cases like a task that's too long to fit, duplicate tasks, or an owner with zero available time, so those could still hide bugs.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The scheduling logic came together at the end. The way generate_plan filters by due date first, then sorts by priority, then fills available time felt like the natural flow and was easy to understand and reason about once the classes were set up.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would actually use the owner preferences field in scheduling. Right now it exists on the Owner class but the scheduler never looks at it. I would also fix how mark_task_complete handles recurring tasks, right now only daily and weekly tasks reschedule themselves, so completing an every_other_day or biweekly task quietly does nothing.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
AI is useful for getting a structure up quickly, but you still have to read and understand what it gives you. The class diagram had the Pet and Scheduler relationship backwards, and that would have been a real design problem if it wasn't caught. AI speeds up the work but the judgment still has to come from you.
