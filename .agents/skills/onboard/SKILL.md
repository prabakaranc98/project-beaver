---
name: onboard
description: Set up a learner's Beaver workspace on first run, or after a major change of direction. Asks at most seven questions and drafts a direction, seed capabilities and a first challenge. Use when there is no Beaver home yet or the learner says their goal has changed.
---

## Inputs
- The learner's answers
- Optional: a resume or profile export, only if the learner offers it

## Procedure
Ask one question at a time, at most seven:
1. Which track is home (data, ML, AI, product, platform), and which role are you aiming for?
2. By when?
3. How many focused hours a week can you give?
4. Which projects have you already built? Links are welcome.
5. Which part of the work do you avoid or find hardest?
6. How much help do you want by default? (Socratic, Hint, Example, Pair or Delegate)
7. Is any of your work confidential, and what monthly model budget do you want?

Then:
- Draft a direction and seed capabilities from the answers. Every resume line or self-description is a claim at level 0 until an artifact backs it. Keep claimed and evidenced levels apart.
- For each project they named, draft a registry entry with its local path, `access: read-only` and the privacy they stated.
- Suggest one first challenge they could start within the hour, and name the first action.

## Output
Drafts in `generated/drafts/`: `direction.md`, `capabilities/`, `registry.yaml`, `now.md`. Mark each with your name, model and help level. The learner moves what they accept into `learner/` and `projects/`, then runs `beaver init`.

## Boundaries
- Write only to `generated/drafts/`.
- Do not send a resume to a model unless the learner's privacy answer allows it.
- Do not assign a skill level from a resume, a title or years of experience.
- The learner picks the goal and the first challenge; you offer one option and ask.
