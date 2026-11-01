# Contributing to Beaver

Beaver is built in the open and dogfooded from day one. Every change, including the author's, follows the loop below. The full plan is in [`docs/build-plan.md`](docs/build-plan.md); this page is the working checklist.

## The loop

1. **Issue first.** Every change starts from an issue with a milestone, labels, a size and a done-when line. Use the *Feature or task* template.
2. **Branch** from `main`: `feat/<issue>-<slug>`, `docs/<issue>-<slug>`, `test/<issue>-<slug>` or `chore/<issue>-<slug>`.
3. **Commit** with Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`.
4. **Open a PR** for one issue only. Link it with `Closes #n`, put it on the issue's milestone, and fill in the template.
5. **CI** (`ci / check`) must be green. It checks the PR title, validates the example workspace, and runs the tests.
6. **Squash merge.** The PR title becomes the commit on `main`, so `main` reads like the changelog.

## Before you ask for a merge

- [ ] The PR title follows Conventional Commits; CI enforces it
- [ ] The template is filled in: principle served, illusion test, how it was tested, docs, token cost
- [ ] The self-review checklist is ticked
- [ ] Once a pilot or another contributor joins, one more reviewer approves

## Testing

| Layer | What | When |
| --- | --- | --- |
| Unit | Parsing, schemas, ID resolution, status math, WIP limits (`pytest`) | Every PR, in CI |
| Fixture snapshots | `validate` and `status` on `healthy`, `broken-links`, `stalled` and `over-limit` workspaces; a diff against `tests/golden/` fails | Every PR, in CI |
| Skill evals | Each skill on three scenarios: writes only to `generated/`, cites files, ends with one action, stays under its token cap | Before each release |
| Dogfood acceptance | Build ratio, blind brief review, friction count, pilot debrief | At each milestone gate |

A bug fix comes with a test that fails before the fix.

## Friction while dogfooding

Anything confusing, slow, noisy or missing becomes a *Dogfood friction* issue the same day, one issue per friction. The backlog is triaged every Sunday.

## Milestones and releases

- A milestone closes when its exit criteria are met, never just because the date has passed. Each gate (go, adjust or kill) is written up in `DECISIONS.md`.
- Releases follow semantic versioning and stay at 0.x until a pilot finishes a full loop without the author's help.
- Each release uses the *Release* issue template: CHANGELOG entry, tag, release notes with an upgrade section.
- A schema change bumps `schema_version` and ships with a migration note.
