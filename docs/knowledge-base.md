# Knowledge base and curriculum

This tab is the seed of `core/knowledge/fde/` and the FDE role pack: what forward-deployed work is, what to learn, how a project builds that learning, and how others read the result.

## 1. The FDE landscape

The role started at Palantir and is now hired for across AI labs, data platforms, CRM vendors and startups. The title is the same, but what gets deployed differs, and so does the craft each company weights most. Everything below comes from current job postings.

| Company | What their FDEs do | Craft weighted most | A project that signals fit |
| --- | --- | --- | --- |
| [Palantir](https://jobs.lever.co/palantir/98b81271-9e15-40b7-8dce-0c62f24702f9) | Work directly with customers to understand their biggest problems, then design and implement data-driven solutions; [embed until the problem is theirs](https://jobs.lever.co/palantir/b4aa51a2-bc43-4d67-bf55-12db7feefb3a) | End-to-end ownership in small teams; data to operational decisions | An operational app built on a data model that changes how a workflow runs |
| [OpenAI](https://jobs.a16z.com/jobs/openai/e9d435e1-1b9e-4715-84ce-75f372e5559c--forward-deployed-engineer-uae) | Lead complex deployments of frontier models in production; [own discovery, scoping, design, build and rollout](https://seedtable.com/jobs/2762), measured by production adoption | Delivery under ambiguity; turning field signal into platform capability | A model deployment with discovery notes, an adoption metric and a pattern write-up |
| [Anthropic](https://agentic-engineering-jobs.com/jobs/anthropic-forward-deployed-engineer-applied-ai-uk-yiEH3A) | Embed with strategic customers in the Applied AI team; production LLM work including prompting and evaluation; document repeatable deployment patterns | Evaluation, agent development, reusable patterns | An agent with an eval suite and a written deployment pattern |
| [Databricks](https://startup.jobs/sr-forward-deployed-engineer-databricks-8030464) | Embed with strategic customers to design and deliver full-stack data and AI applications on the Databricks platform, owning the architecture | Data engineering at scale, secure architecture, stakeholders from engineers to C-level | A governed data pipeline feeding an AI application, with an architecture diagram |
| [Salesforce](https://jobs.omegavp.com/companies/salesforce-2/jobs/86049436-forward-deployed-engineer) | Design, build and deploy agentic solutions inside enterprise customer environments, paired with a Deployment Strategist; field edge cases become product features | Agents inside existing business systems; field-to-product feedback | An agent integrated with a CRM-style system of record, with edge cases logged |
| AI startups | a16z has called the FDE [the hottest job in startups](https://entrepreneurloop.com/?p=5231), part of a services-led growth model | Speed to value, breadth, founder-like ownership | A pilot that reached real users fast, with honest notes on what didn't work |

**Market signal.** Indeed and Financial Times analysis found applied AI and FDE postings [rose more than 800% between January and September 2025](https://www.storyboard18.com/digital/openai-anthropic-hire-engineers-who-can-code-and-communicate-with-customers-83622.htm). Adjacent titles such as Solutions Architect, Agent Engineer and Technical Delivery Engineer [describe similar work](https://thepixelpioneers.blogspot.com/2025/08/what-are-forward-deployed-engineers-and.html), so a learner should search beyond the literal title.

## 2. What every company asks for

Read side by side, the postings converge on five threads. None of them is "knows framework X." Each one is a habit that projects can build and evidence can show.

| Thread | Pillar | What it looks like in practice | Beaver practice area |
| --- | --- | --- | --- |
| Own it from first conversation to production | Ethos | Discovery notes, a brief, a shipped system and a handoff, all by the same person | Identify → Define → Build |
| Talk to everyone, from engineers to the C-suite | Pathos | A stakeholder map, an exec one-pager and an operator runbook for the same project | Communicate |
| Production-grade data and AI, with evaluation | Logos | Eval sets, failure handling, security, cost per outcome | Build → Evaluate |
| Turn field lessons into reusable patterns | Ethos + Logos | A written deployment pattern drawn from two or more projects | Communicate → Illustrate |
| Calm judgment in ambiguity | Ethos + Pathos | Decision records made with incomplete information, revisited later | Define → Shape |

**The insight for learners.** A strong FDE portfolio is not a list of technologies. It is evidence of these five threads, which is exactly what Beaver's evidence levels and case studies are built to show.

## 3. Curriculum: nine modules

The FDE curriculum has nine modules in a suggested order. Each module is learned through a project, never as a course alone. A learner's `shape-curriculum` run reorders and skips modules based on their own evidence.

| # | Module | Concepts | Pillar | A project that teaches it | Why companies care |
| --- | --- | --- | --- | --- | --- |
| 1 | Systems thinking for enterprise problems | Feedback loops, coupling, nonlinearity, stakeholders as part of the system | Logos + Pathos | Map one real workflow as a system before touching code | Client problems are interconnected; local fixes break other things |
| 2 | Discovery and problem definition | Interviewing, problem statements, scoping, non-goals, done-when | Pathos + Ethos | Turn a vague request into a one-page brief | FDEs own discovery and scoping |
| 3 | Data foundations | Modeling, quality checks, contracts, lineage, access control | Logos | Build one trusted table from three messy exports | Every AI system inherits its data's flaws |
| 4 | Applied LLM engineering | Prompting, retrieval, tool use, agents, structured outputs | Logos | An agent that survives partial tool failure | The core build skill in AI deployments |
| 5 | Evaluation | Eval sets, metrics, LLM-as-judge calibration, regression tests | Logos + Ethos | An eval harness built from real examples | Evaluation is named in AI-lab FDE requirements |
| 6 | Production and platform | Deployment, observability, security, permissions, cost and latency | Logos | A model behind an API with timeouts, logs and cost per call | Systems must run without their author |
| 7 | Adoption and change | Pilots, training, feedback loops, adoption metrics | Pathos | A two-week pilot with three users and one adoption metric | Success is measured by production adoption |
| 8 | Communication and illustration | Exec memos, demos, architecture diagrams, decision records | Pathos + Ethos | A one-page recommendation plus one system diagram | FDEs engage stakeholders up to the C-suite |
| 9 | Field to product | Pattern extraction, reusable playbooks, product feedback | Ethos + Logos | A deployment pattern written from two projects | Field lessons become platform features |

Modules 1–2 come first for everyone. Each track then emphasizes different modules: data leans on 3, AI on 4–5, platform on 6, and product on 7–8. Module 9 is where a builder becomes a practitioner.

## 4. Anatomy of an FDE-grade project

An FDE-grade project has all three layers. A tutorial project usually has only logos, and the missing layers are why it doesn't read as forward-deployed work.

| Layer | Questions the project must answer | Artifacts that prove it |
| --- | --- | --- |
| Pathos: the people | Who has the problem? What does it cost them? Who decides, who uses it, who could block it? | Stakeholder map, interview notes, brief with a named user |
| Logos: the system | What is the system around the problem? What data is real? What breaks first? How do we know it works? | System map, `DECISIONS.md`, `EVAL.md`, tests, failure handling |
| Ethos: the stance | What did we promise and not promise? What are the limits? Can someone else run it? | A limitations section, a runbook, explained evidence, an honest case study |

**The project learning card.** Every brief starts with this card, so the learning is designed in rather than discovered by accident.

```markdown
## Learning card: crm-sync
I will learn:        idempotency, retries under timeouts, writing an exec one-pager
Capabilities:        capability.api-integration (target level 3), capability.exec-communication (level 2)
Modules:             3 Data foundations, 6 Production, 8 Communication
Evidence I'll produce: retry tests, a decision record, a one-page recommendation
Who would care:      Databricks/Salesforce-style FDE leads (integration), any client lead (one-pager)
What would make this a tutorial instead: no real user, no failure cases, no handoff
```

## 5. Worked example: beyond simple RAG

The same idea, a support copilot, can be a weekend demo or a piece of forward-deployed work. The model code is similar in both; everything around it is what makes it FDE-grade. The numbers below are illustrative targets, not benchmarks.

| Dimension | Typical RAG demo | FDE-grade version |
| --- | --- | --- |
| Problem | "Chat with our docs" | Cut time to first useful reply on tier-1 tickets, as agreed with the support lead |
| Users | None named | Three support agents and their team lead, interviewed before building |
| Data | PDFs dumped into a vector store | Past tickets plus the knowledge base, with freshness dates and per-document permissions |
| Retrieval | Top-k similarity | Hybrid search, filtered by product and by what the user may see |
| Evaluation | Eyeballing a few answers | For example, 150 labeled real tickets: answer correctness and citation correctness, with an LLM judge checked against human labels |
| Failure handling | Always answers | Abstains below a confidence threshold and escalates to a human |
| Security | None | Respects document permissions and redacts personal data |
| Cost and latency | Unknown | Cost per resolved ticket and p95 latency, tracked |
| Adoption | A demo video | A two-week pilot: usage rate and how often agents override the draft |
| Handoff | None | Runbook, limitations section, decision log |
| The story | "I built a RAG app" | "Tier-1 replies got faster in a pilot, here's the eval, and here's what didn't work" |

**What the learner gains:** modules 2, 4, 5, 6, 7 and 8 in a single project, with evidence for most of them at level 2 or above. **What the demo version gains:** familiarity with one library.

## 6. Three lenses on the same project

The same project is read differently by each audience. Beaver makes sure each reader finds the artifact they look for, without the learner writing five versions.

| Reader | What they look for | What convinces them | Beaver artifact |
| --- | --- | --- | --- |
| The learner | What did I actually learn, and what's next? | Evidence that moved up a level; questions that evolved | Reflections, evidence levels, inquiry log |
| An engineer peer | Were the decisions sound and the trade-offs explicit? | Tests, failure handling, a readable decision log | `DECISIONS.md`, `EVAL.md`, tests |
| An FDE lead or hiring manager | Can this person own a messy problem end to end? | Discovery to production by one person, communicated clearly | Brief, stakeholder map, case study |
| A founder | Do they get to value fast and bring lessons back to the product? | Speed to a real pilot; a reusable pattern | Adoption metric, pattern write-up |
| A client leader | Will this solve my problem safely, at a cost I accept? | Outcome, risk, cost in plain words | One-page recommendation, cost per outcome |

The case study template has one section for each of the last four readers, and the learner's reflection serves the first.

## 7. Seed project library

Eight projects cover all five tracks and all nine modules. Each one becomes a challenge brief in the role pack, with a learning card already filled in.

| Project | Track | Modules | What you learn | Who would recognize it |
| --- | --- | --- | --- | --- |
| Support copilot beyond RAG | AI | 2, 4, 5, 6, 7, 8 | Retrieval with permissions, evals, abstention, adoption | AI labs, CRM and support platforms |
| One trusted table from messy exports | Data | 1, 3, 8 | Data contracts, quality checks, lineage, explaining data to non-engineers | Data platforms such as Databricks and Palantir |
| An agent that survives partial failure | AI, Platform | 4, 5, 6 | Idempotency, retries, tool design, recovery traces | AI labs, agent startups |
| An operational app on a data model | Data, Product | 1, 3, 7 | Turning a data model into a workflow people use daily | Palantir-style deployments |
| From forecast to decision | ML, Product | 1, 2, 8 | Forecasting, causal reasoning, framing a decision rather than a prediction | Decision science and consulting teams |
| A calibrated LLM-as-judge harness | AI | 5, 9 | Eval design, agreement with human labels, regression suites | AI labs, eval-heavy teams |
| A cost and latency budget for an AI workflow | Platform | 6, 8 | Profiling, caching, model routing, cost per outcome | Platforms and startups watching margins |
| A discovery sprint with a real stakeholder | Product | 2, 7, 8 | Interviewing, scoping, writing a recommendation | Every FDE team |

**Order for a first year:** start with the discovery sprint (it needs no code and sharpens every later project), then pick two projects from the learner's home track, then one from another track.

## 8. Insight cards

An insight is a short, testable claim distilled from practice, kept in `learning/insights/` with where it came from, when it holds and when it breaks. Seed insights ship as hypotheses. Learners confirm, refine or overturn them with their own evidence, and that is how the knowledge base stays honest.

| Insight | Holds when | Breaks when | Pillar |
| --- | --- | --- | --- |
| Build the eval before the agent | The task has checkable outcomes | The task is exploratory and its goal isn't settled yet | Logos |
| The data you are promised is not the data you get | Any client data integration | You generated the data yourself | Logos + Pathos |
| Adoption is the metric; accuracy is the entry ticket | Tools that people choose to use | Fully automated back-office flows | Pathos |
| Draw the system before you build it | More than two components or teams | A one-file script | Logos |
| A field edge case is a product signal | You deploy a platform repeatedly | One-off custom builds | Ethos + Logos |
| Say what it can't do before anyone asks | Any stakeholder-facing demo | Never | Ethos |
| The person who complains loudest is rarely the person who decides | Organizations with several layers of stakeholders | Single-founder clients | Pathos |

```markdown
---
id: insight.eval-before-agent
claim: Build the eval before the agent.
from: [project.support-copilot, core/knowledge/fde/logos/evaluation]
holds_when: the task has checkable outcomes
breaks_when: the task is exploratory and its goal isn't settled yet
status: confirmed        # hypothesis | confirmed | refined | overturned
evidence: [evidence.copilot-eval-harness]
---
```

## Sources

Job postings and articles as found on 2026-11-01; postings change often.

- [Palantir: Forward Deployed Software Engineer](https://jobs.lever.co/palantir/98b81271-9e15-40b7-8dce-0c62f24702f9)
- [Palantir: Forward Deployed Software Engineer, New Grad](https://jobs.lever.co/palantir/b4aa51a2-bc43-4d67-bf55-12db7feefb3a)
- [OpenAI: Forward Deployed Engineer (UAE), via a16z jobs](https://jobs.a16z.com/jobs/openai/e9d435e1-1b9e-4715-84ce-75f372e5559c--forward-deployed-engineer-uae)
- [OpenAI: Forward Deployed Engineer (Dublin)](https://seedtable.com/jobs/2762)
- [Anthropic: Forward Deployed Engineer, Applied AI (UK)](https://agentic-engineering-jobs.com/jobs/anthropic-forward-deployed-engineer-applied-ai-uk-yiEH3A)
- [Databricks: Sr. Forward Deployed Engineer](https://startup.jobs/sr-forward-deployed-engineer-databricks-8030464)
- [Salesforce: Forward Deployed Engineer](https://jobs.omegavp.com/companies/salesforce-2/jobs/86049436-forward-deployed-engineer)
- [What is a Forward Deployed Engineer? (a16z "hottest job")](https://entrepreneurloop.com/?p=5231)
- [OpenAI, Anthropic hire engineers who can code and communicate with customers](https://www.storyboard18.com/digital/openai-anthropic-hire-engineers-who-can-code-and-communicate-with-customers-83622.htm)
- [What are Forward Deployed Engineers, and why are they so in demand?](https://thepixelpioneers.blogspot.com/2025/08/what-are-forward-deployed-engineers-and.html)
