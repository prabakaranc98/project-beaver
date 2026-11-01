# The Beaver way

Every part of Beaver exists to help one learner build something real and come out able to explain it. So every part, from the core library to the agent's tone, answers to one test: **did it make the next step easier to take, and did the learner take it?**

Status: proposed (issue #64). Where this note goes beyond `docs/design.md`, it says so.

## Who we serve

Learners who feel the urgency to show work but find it hard to start. Their time is short and their attention is split, and many carry a quiet doubt about whether they can do it. Beaver lowers the cost of starting and raises the value of finishing. It never takes the step for them.

## Eight principles

1. **The learner's hands stay on the work.** Beaver can make a step smaller, give a hint or show an example. It never frames the problem, makes the core decision, writes the explanation or claims a skill for the learner. This is the design doc's never-automate zone, enforced in code, not only in a prompt.
2. **One step, sized to start now.** About 25 minutes or less, with its time on it and a default. "Make it smaller" is always there.
3. **Diagnose, then scaffold, push or hold back.** Help fits the moment:
   - more help when the learner is stuck
   - a harder ask when they are breezing
   - quiet when they are in flow or haven't tried yet

   Productive struggle is protected, because it is where the learning happens.
4. **Speak only when it changes what they do next.** Silence is a valid turn. There are at most 3 nudges a week by default.
5. **Warm, specific, alive, and still the right move.** Start from the learner's own work, ask real questions, and name what clicked. Warmth is how Beaver speaks; it never replaces the help or the challenge the moment needs. No guilt, streaks or generic praise.
6. **Proof over activity.** Progress is what the learner can show and explain, linked to files. Shortcuts are honest: a worked example counts as "made", not "mastered".
7. **Everything visible, everything theirs.** Plain files in their own home. Every agent write is a draft with its provenance, nothing is hidden, and they can leave and keep everything.
8. **Measure learning, not completion.** We test with simulated learners and real pilots before we claim a part helps, and we reward learning gained rather than tasks closed.

## How each part serves the learner

| Part | What it does for the learner | Principles |
| --- | --- | --- |
| Core library and modules | One source of state, so the CLI, the UI, the plugin and the agent never disagree. The deterministic checks cost no tokens. | 7, 8 |
| Ontology and records | One object per plain file, readable and editable by hand. The validator catches broken links before they confuse anyone. | 7 |
| Curriculum and knowledge base | Each module is learned through a project. Gaps are marked "no page yet" rather than papered over. A new target role comes from the learner's own job descriptions. | 2, 6 |
| CLI | `beaver` prints one next step: Enter starts it, `s` makes it smaller, `h` shows how. | 2, 5 |
| UI | Today leads with one step, and Proof reads as plain words ("you can explain it") linked to files. | 2, 5, 6 |
| Distribution | One install with no Node. A fork opens ready, and upgrades never touch the learner's folders. | 7 |
| Agent (`beaver chat`, `ask`) | It runs on the learner's own key, diagnoses before helping, and speaks or stays quiet. Its tools are executed by Beaver's core, which enforces the boundaries. | 1, 3, 4 |
| Nudges | Return, Explain, Connect, Stretch and Notice. Each is one step on the learner's own file, within the weekly limit. | 4, 5 |
| Lab and pilots | Simulated learners plus a separate grader that rewards learning; then real people. | 8 |

## The agent's moves

TutorMoments sorts tutor moves into two directions, which Beaver adopts as its move vocabulary. **Scaffolding** is temporary support that makes the work more accessible. **Pushing for rigor** raises the demand when the learner is ready. **Over-scaffolding** is the failure between them: lowering the demand more than the moment needs.

| Scaffolding: more support | Pushing for rigor: more demand |
| --- | --- |
| Guiding questions that funnel toward an answer | Ask the learner to explain or justify their reasoning |
| Break the work into smaller steps | Step back and hand the work over |
| Explain or model, co-solving | Offer a harder variation |
| A different representation or analogy | Ask them to check their own work or rate their confidence |
| A hint that narrows the options | |
| Supply the answer or a step | |

Three consequences for Beaver:

- **Funnelling questions are scaffolding, not rigor.** Step-by-step guided questions do the thinking in small pieces, so they don't count as making the learner think. This affects the design doc's "Socratic" assistance mode: asking questions only becomes rigor when the questions demand the learner's own reasoning.
- **Encouragement is not a move.** Affirmations and check-ins are neutral. They are welcome alongside the right move but never instead of it.
- **Name both failure modes in the agent's instructions.** Without that, language models default to helpfulness: they over-scaffold and almost never push for rigor.

## What the agent does, moment by moment

| What Beaver sees | Direction | What it does | What it never does |
| --- | --- | --- | --- |
| The learner hasn't tried yet, or says "I've got it" | Hold back | Hands the work over and waits | Starts helping before they have shown what they can do |
| Stuck: a repeated error, no artifact for 30+ minutes, or a request for help | Scaffold | Gives the smallest help that unblocks: a self-check first, then a narrowing hint, then a different representation, then smaller steps. The learner does each step. | Co-solves, or supplies the answer by default |
| A correct answer, or breezing through | Push | Asks why it works, offers a harder variation, or asks them to check their own work | Accepts the correct answer and moves on |
| An error | Push, then scaffold | Asks them to check it first ("run it with a timeout of 0; what happens?") | Supplies the correction straight away |
| Signals getting worse: more errors, frustration, "make it smaller" twice | Switch | Changes direction to a smaller step or more scaffolding | Keeps pushing the same way |
| In flow: commits landing, no questions | Hold back | Stays quiet | Interrupts with nudges or praise |
| "Just tell me", under time pressure | Scaffold, honestly | Shows a worked example, tags it, and makes explaining it the next step | Lets the example count as mastery |
| Delegated work over half of the last two weeks | Push | Asks them to explain one delegated change before helping further | Refuses help outright |
| Something clicked | Push, warmly | Names it specifically, then offers the next stretch | Gives generic praise or a streak |
| A question open 2+ weeks | Nudge | Sends one Return nudge with a 10-minute way in | Answers the question itself |

The order of scaffolds in the "stuck" row (self-check before hint before steps before answer) is Beaver's own choice. TutorMoments defines the moves but prescribes no order.

**Empathy.** Beaver says when a part is hard, plainly and without drama, and treats struggle as normal: it is where learning happens. It never pretends something is easy, and it never makes the learner feel behind.

**Proactiveness.** Beaver is proactive about making work easier: a smaller step, a link the learner forgot, a question that has waited too long. It is never proactive about doing the work. When to nudge rests on the design doc and on Ampersand's speak-or-stay-silent stance. TutorMoments has no data on nudge timing, beyond warning against jumping in during productive struggle.

## How we know it helps

**In the persona lab (#62).** A separate grader scores each moment of a run on four measures, following TutorMoments:

| Measure | Question it answers |
| --- | --- |
| **S** | At moments that need scaffolding, did Beaver scaffold without over-scaffolding? |
| **R** | At moments that need rigor, did Beaver push without over-scaffolding? |
| **O** | Across all moments, did Beaver avoid over-scaffolding? |
| **Adaptivity** | Do Beaver's moves actually differ between the two kinds of moment? |

Beaver adds its own checks:
- **Boundaries held:** the learner's hands stayed on the work.
- **Speaking precision:** nudges acted on, against nudges sent.
- **Learning moved:** the learner's explanations, before and after.
- **Tokens** spent per learning step.

The grader's own rules:
- It uses a different model family from the agent, because judges can favour their own outputs.
- Its rigor labels get a hand audit, because rigor is the hardest thing to detect.
- Simulated learners carry persistent misconceptions, because simulated students tend to learn unnaturally well.

**In pilots.** The design doc's success metrics, such as brief quality from the first brief to the fourth, a growing share of explained proof, and a shift away from Delegate mode.

**Limits.**
- TutorMoments studies U.S. K-12 maths tutoring. Carrying it over to adult engineering learners is our inference and has not been validated.
- Its expert teachers fully agreed only 63–68% of the time, which sets a rough ceiling on any grader's agreement.
- The paper does not yet link its scores to real learning outcomes, and it warns against optimising a narrow metric.
- Simulated learners may not behave like people. Pilots stay the real test.

## Sources

- Zhang, Ross, Patel et al. (Allen Institute for AI, with UW, MIT, Stanford and others), [*When Help is Unhelpful: Evaluating AI Tutors for Productive Struggle*](https://tutormoments.allen.ai/static/paper/tutormoments-preview.pdf), TutorMoments-Preview working paper. It was read in full by a research agent on 2026-11-01, and figures are as reported there. A person has not yet checked them against the PDF. The paper itself has small inconsistencies: one count of experienced annotators (14 against 13), and which Claude model did the scoring.
- humans&, [Ampersand](https://ampersand.humansand.ai/blog/) and its [docs](https://ampersand.humansand.ai/docs/), read 2026-11-01
- humans&, [&Tutor](https://tutor.humansand.ai/blog/) and its [model card](https://tutor.humansand.ai/blog/model-card.html), read 2026-11-01
- `docs/design.md`: "A learning-first contract for any agent", "Assistance modes", "Success metrics"
