---
name: frame-challenge
description: Help the learner frame a piece of work as a one-page brief before building. Use when starting any project, feature or experiment. Asks questions and drafts from the learner's answers; it does not frame the problem for them.
---

## Inputs
- The learner's idea, in their own words
- `core/templates/brief.md` and the learner's target capabilities (`learner/capabilities/`)

## Procedure
Run `beaver doctor` first to find the Beaver home folder; every path below is inside it.
1. Ask who has the problem, by role, and what it costs them today. Wait for the answer.
2. Ask what changes for that person when it works. One sentence they would agree with.
3. Ask for at least one non-goal, and one constraint if there is one.
4. Ask how someone else could check it is done. Push until the check is something a person can run.
5. Draft the brief from the learner's answers only. Mark every field they did not answer as `<open>`; do not fill it in.
6. Name the weakest part of the brief in one line, and ask one question about it.

## Output
`generated/drafts/brief-<slug>.md`, using `core/templates/brief.md`. Mark it with your name, model and help level. The learner moves it to `projects/briefs/` when they accept it.

## Boundaries
- The learner frames the problem. Never supply the user, the outcome or the done-when yourself; ask, then hand it back.
- Write only to `generated/drafts/`.
- Check the active-project limit in `projects/registry.yaml` and say so if this brief would go over it.
