---
name: Release
about: Cut a release at the end of a milestone
title: "Release v0."
labels: release
---

**Milestone gate**
- [ ] Exit criteria in `docs/build-plan.md` met, not just the date passed
- [ ] Gate note in `DECISIONS.md`: go, adjust or kill, with reasons

**Release checklist** (from `docs/build-plan.md`)
- [ ] CI green on `main`
- [ ] Skill eval checklist passed
- [ ] The example workspace validates
- [ ] Pracha's own workspace upgrades cleanly
- [ ] Docs updated
- [ ] Schema changed? `schema_version` bumped, with a migration note

**Ship**
- [ ] `CHANGELOG.md` entry, drafted from the Conventional Commits since the last tag and edited by hand
- [ ] Tag `v0.x.0` on `main`
- [ ] GitHub release notes, with an upgrade section
