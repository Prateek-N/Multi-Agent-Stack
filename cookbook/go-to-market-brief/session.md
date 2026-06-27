---
domain: marketing
phases: 0–5
task: Go-to-market strategy brief — agents-maker Product Hunt launch
budget: $0 (organic only)
launch_date: T-14 days
target: Senior engineers at 20–200 person startups
---

# Session: Go-to-Market Brief — agents-maker Product Hunt Launch

## CLI Invocation

```bash
python generate_prompt.py \
  --domain marketing \
  --task "Write a go-to-market strategy brief for agents-maker launching on Product Hunt in 2 weeks. Target: senior engineers at 20-200 person startups frustrated with inconsistent AI output quality. Budget: $0 organic only. Stack: GitHub, HuggingFace Spaces demo, X/Twitter, HackerNews." \
  --phase 0
```

---

## Generated Prompt

```
## Project Context
Project   : agents-maker
Repo      : github.com/org/agents-maker
Version   : 0.4.1-beta
Stack     : Python, Claude API, LangGraph, YAML config
Demo      : huggingface.co/spaces/org/agents-maker-demo

## Session State
Phase     : 0 (Task Framing)
Previous  : None
Artifacts : None

## Task
Write a go-to-market strategy brief for agents-maker launching on Product Hunt
in 14 days. Constraints: $0 budget, organic channels only (GitHub, HuggingFace
Spaces, X/Twitter, HackerNews). Target audience: senior engineers at 20–200
person startups who are frustrated with inconsistent AI output quality.

Deliverable: A complete GTM brief covering ICP, positioning, messaging
framework, channel plan, launch timeline, and success metrics.

## Domain & Routing
Domain    : marketing
Sub-type  : launch strategy / product positioning
Complexity: medium-high (multi-channel, tight timeline, zero budget)
Route to  : orchestrator → architect_agent → execution_agent → reviewer_agent
```

---

## Phase 0 — Task Framing

**Agent: orchestrator**

Before routing this to architect, I need to lock two things: ICP sharpness and
launch scope. Broad ICPs kill organic launches because the message dilutes to
nothing. Let me frame the constraints and confirm assumptions.

**Scoping questions surfaced:**

1. Is the primary pain point "inconsistent output quality" (correctness) or
   "unpredictable agent behavior" (reliability)? These require different hooks.
2. Are we optimizing the Product Hunt launch for upvotes (social proof play) or
   inbound GitHub stars (acquisition play)? Both are organic but the call-to-
   action differs.
3. What does "senior engineer at a 20–200 person startup" mean in behavioral
   terms — are they the decision-maker or the champion selling upward?

**ICP Confirmation (from task brief):**

- Title: Staff / Senior / Lead Engineer, occasionally Head of Engineering
- Company size: Series A–B, 20–200 employees
- Pain: They've shipped an AI feature; it works 70% of the time; the other 30%
  produces hallucinations, wrong formats, or silent failures that reach prod
- Motivation: They want deterministic, reviewable agent pipelines — not another
  "just prompt it better" wrapper
- Decision authority: They can star a repo and open-source adopt without budget
  approval; paid adoption needs eng manager sign-off

**Scope locked:**
- Launch window: 14 days
- Primary conversion goal: GitHub stars + HuggingFace demo runs
- Secondary goal: HN Show HN front page within launch week
- Product Hunt goal: Top 5 of the day (not #1; #1 requires a warmed audience)

---

> **[Companion]** Phase 0 complete. ICP and launch goals confirmed. Routing to
> architect_agent for campaign strategy outline.

---

## Phase 1 — Requirements

**Agent: architect_agent**

Received: ICP + scope from orchestrator. My job here is to define the campaign
architecture — what frameworks apply, what the channel hierarchy is, and what
success looks like numerically.

**Applicable Frameworks:**

- **Positioning**: April Dunford's "Obviously Awesome" — context, competitive
  alternatives, unique attributes, value for target, category
- **Messaging**: Jobs-to-be-Done hook → pain → proof → CTA
- **Channel hierarchy** (zero-budget constraint forces sequencing):
  1. Owned: GitHub README, HuggingFace Space description
  2. Seeded communities: HackerNews Show HN, relevant subreddits (r/MachineLearning, r/LocalLLaMA)
  3. Distribution amplifiers: X/Twitter thread from founder + repost network

**Campaign Architecture:**

```
T-14  Positioning & messaging locked
T-10  GitHub README rewrite shipped
T-7   HuggingFace demo polished; teaser thread drafted
T-3   HN Show HN post drafted; PH assets prepared
T-1   Notify personal networks; embargo lifted for friendly upvoters
T-0   Product Hunt goes live 12:01 AM PT; HN Show HN 9 AM ET
T+1   Follow-up X thread with "what we learned" angle
T+7   GitHub star count shared as social proof; blog post optional
```

**Numeric Targets (realistic for organic, zero-budget):**

| Metric | Target |
|--------|--------|
| PH upvotes (launch day) | 200–400 |
| GitHub stars (T+7) | +300 |
| HF demo runs (T+7) | 500 |
| HN points | 80+ (front page threshold ~60) |
| X/Twitter impressions | 50K across thread |

**Risk:** Product Hunt launch day is a Thursday. If the date is a weekend,
shift to Tuesday. Weekends underperform for developer tools by ~40%.

---

> **[Companion]** Phase 1 complete. Campaign architecture, framework selection,
> and numeric targets defined. Routing back to architect_agent for messaging
> framework and channel plan detail.

---

## Phase 2 — Solution Design

**Agent: architect_agent**

Now designing the actual messaging framework and per-channel content plan.
Everything anchors on the positioning statement first.

**Positioning Statement (April Dunford format):**

> For **senior engineers building AI features at growth-stage startups**
> who are frustrated that **their LLM pipelines produce inconsistent, hard-to-
> debug output in production**, agents-maker is a **structured multi-agent
> orchestration framework** that **makes agent behavior reviewable, repeatable,
> and correctable** — unlike rolling your own LangChain setup or using
> opinionated SaaS wrappers that hide the logic from you.

**Message Hierarchy:**

| Level | Copy |
|-------|------|
| Hero (7 words) | "Consistent AI agents. No black box." |
| Sub-headline (1 sentence) | "agents-maker gives your LLM pipelines a structured phase model so you can see exactly why an output changed — and fix it." |
| Proof point 1 | Open-source, MIT licensed — you own the logic |
| Proof point 2 | YAML-configured phase routing — readable by any engineer on your team |
| Proof point 3 | Drop-in Claude API integration with caching built in |

**Objection Handling:**

- "We already use LangChain" → agents-maker is not a replacement; it's the
  coordination layer above your chains
- "We don't have time to learn another framework" → 15-minute HuggingFace demo;
  if you can't run a working agent in 15 min, we failed
- "Why not just use CrewAI / AutoGen?" → Those are role-playing frameworks;
  agents-maker is phase-structured — deterministic routing, not emergent

**Channel Plan:**

**GitHub README (owned, T-10)**
- Above the fold: hero message + one-line install (`pip install agents-maker`)
- Section: "Why agents-maker exists" — 3-paragraph pain narrative
- Section: "5-minute quickstart" with copy-paste example
- Badges: PyPI version, HuggingFace demo link, license

**HuggingFace Spaces Demo (owned, T-7)**
- Title: "agents-maker — Try structured multi-agent orchestration in browser"
- Description rewritten to match positioning statement
- Default example: GTM brief generator (dogfoods the tool, meta-appeal)
- Add "Deploy to your own Space" button

**X/Twitter Thread (distribution, T-0)**
- Tweet 1 (hook): "We shipped 3 AI features last year. All 3 had the same bug:
  nobody could explain why the output changed between runs. Here's what we built
  to fix that. 🧵"
- Tweet 2: The pain in concrete terms (prod incident, customer complaint)
- Tweet 3: The solution (phase model diagram image)
- Tweet 4: Demo GIF from HuggingFace Space
- Tweet 5: GitHub link + "We're #X on Product Hunt today — link in bio"
- Tweet 6: Ask ("If this resonates, a ⭐ on GitHub takes 4 seconds")

**HackerNews Show HN (seeded, T-0 9 AM ET)**
- Title: `Show HN: agents-maker – structured multi-agent pipelines with
  phase-based routing (open source)`
- Body: 3 paragraphs — what it is, why we built it (pain story), what's next
- Comment strategy: founder replies to every comment within 2 hours launch day

---

> **[Companion]** Phase 2 complete. Positioning statement, message hierarchy,
> objection handling, and per-channel content plan designed. Routing to
> execution_agent for full GTM brief draft.

---

## Phase 3 — Implementation

**Agent: execution_agent**

Drafting the full GTM brief document as the primary artifact. All content
anchors on the positioning and channel plan from Phase 2.

*(See **Final Artifact** section below for the complete brief.)*

Structural decisions made during drafting:
- Brief is self-contained; a new hire or contractor could execute from it alone
- Launch checklist is sequenced by calendar day, not by workstream
- Each channel section includes the exact copy to use (no "write something here"
  placeholders)
- Metrics section includes a "call it a success if" threshold for the founder
  who will be too sleep-deprived to compute ratios on launch day

---

> **[Companion]** Phase 3 complete. Full GTM brief drafted. Routing to
> reviewer_agent for brand clarity and message consistency review.

---

## Phase 4 — Review

**Agent: reviewer_agent**

Reviewed the full brief draft against three axes: (1) message consistency
across channels, (2) ICP fit — does every claim land for a senior eng at a
Series A startup, (3) execution realism — can one person actually do this in
14 days with $0.

**Findings:**

| # | Severity | Finding | Resolution |
|---|----------|---------|------------|
| 1 | High | HN title uses "phase-based routing" — jargon not in ICP's vocabulary. They say "predictable" and "debuggable," not "phase-based." | Revised to: `Show HN: agents-maker – open-source multi-agent framework for predictable, debuggable LLM pipelines` |
| 2 | Medium | X thread Tweet 1 uses 🧵 emoji — fine for consumer Twitter, reads as noise in dev-heavy feeds. | Removed emoji; kept the hook copy. |
| 3 | Medium | HuggingFace demo default example is a GTM brief generator — clever but requires the user to know what a GTM brief is. Misses engineers. | Changed default example to: code review multi-agent pipeline (directly in ICP's daily workflow). |
| 4 | Low | Numeric target for HN points (80+) is listed but there's no fallback plan if the post dies at 10 points. | Added: "If <30 points at 2 hours, post a direct link to r/MachineLearning as fallback distribution." |
| 5 | Low | Launch checklist has T-1 "notify personal networks" but no template for what to send. | Added a DM template to the brief. |

**Brand consistency:** Pass. "Consistent, reviewable, correctable" appears in
GitHub, HF, and X copy. Messaging is coherent across channels.

**Verdict:** Ship with revisions 1–3 applied. Items 4–5 are optional hardening.

---

> **[Companion]** Phase 4 complete. Five findings; three high/medium resolved
> in artifact. Routing to orchestrator for handoff and launch checklist.

---

## Phase 5 — Handoff

**Agent: orchestrator**

Brief is approved with reviewer revisions applied. Handing off to the founder
for execution. Below is the prioritized launch checklist.

**Launch Checklist — 14-Day Execution**

```
[ ] T-14  Lock positioning statement with co-founders (30 min sync)
[ ] T-13  Rewrite GitHub README using message hierarchy from brief
[ ] T-12  Update PyPI package description to match hero copy
[ ] T-10  Publish rewritten README; verify all links work
[ ] T-7   Polish HuggingFace Space: new title, description, default example
[ ] T-7   Record 60-second demo GIF for X thread tweet 4
[ ] T-5   Draft HN Show HN post; get 2 engineer friends to sanity-check
[ ] T-5   Draft all 6 X/Twitter thread tweets; schedule for T-0
[ ] T-3   Submit Product Hunt page (hunter: yourself or a PH power user)
[ ] T-3   Prepare PH assets: tagline, description, thumbnail, first comment
[ ] T-1   Send DM template to 20 genuine connections (see brief §7)
[ ] T-1   Brief any co-founders on comment reply strategy for HN
[ ] T-0   PH goes live 12:01 AM PT — do not touch until 8 AM
[ ] T-0   Publish HN Show HN at 9 AM ET
[ ] T-0   Post X thread at 10 AM ET
[ ] T-0   Reply to every HN comment within 2 hours; every PH comment same day
[ ] T+1   Post "what we learned" X thread with star/demo counts
[ ] T+7   Share GitHub star milestone; thank early community
```

**Call it a success if (launch week):**
- PH: 150+ upvotes by end of day
- GitHub: +200 stars
- HN: Front page (any position) for any duration
- HF Demo: 300+ runs

**Escalation:** If HN post fails to gain traction by 11 AM ET, post to
r/MachineLearning (not r/artificial — too consumer-focused).

---

> **[Companion]** Phase 5 complete. Checklist and success thresholds handed
> off. Session artifact follows.

---

---

# Final Artifact: agents-maker GTM Brief

**Document:** Go-to-Market Strategy Brief
**Version:** 1.0 (post-review)
**Owner:** Founding team
**Status:** Approved for execution

---

## 1. Situation

agents-maker is an open-source Python framework for building structured
multi-agent LLM pipelines with deterministic phase routing. It is launching
publicly on Product Hunt in 14 days with no paid marketing budget. Distribution
depends entirely on organic reach across GitHub, HuggingFace Spaces, X/Twitter,
and HackerNews.

The core market insight: every developer who has shipped an AI feature to
production has a story about an output that "just changed" between runs and
took hours to debug. agents-maker is the answer to that story.

---

## 2. Ideal Customer Profile

**Primary ICP — The Frustrated Builder**

- **Title:** Senior Engineer, Staff Engineer, Lead Engineer, Head of Engineering
- **Company:** Series A or B startup, 20–200 employees, has shipped ≥1 AI
  feature to production
- **Pain:** LLM outputs are non-deterministic in ways that matter — format
  breaks downstream parsers, hallucinations reach users, nobody on the team can
  explain why last Tuesday's run produced different results than today's
- **Goal:** A pipeline they can hand off to a junior engineer without a 2-hour
  explanation session
- **Behavior:** Reads HN daily; stars GitHub repos before evaluating; tries
  demos before reading docs; suspicious of SaaS wrappers that hide logic

**Non-ICP (do not target):**
- AI researchers (wrong pain — they want flexibility, not structure)
- Enterprise architects (wrong channel — they don't discover on Product Hunt)
- Hobbyists (wrong motivation — they want magic, not debuggability)

---

## 3. Positioning Statement

> For **senior engineers at growth-stage startups** who are frustrated that
> their **LLM pipelines produce inconsistent, hard-to-debug output in
> production**, agents-maker is an **open-source multi-agent orchestration
> framework** that makes agent behavior **predictable, reviewable, and
> correctable** — unlike DIY LangChain setups that work until they don't, or
> opinionated SaaS platforms that hide the routing logic from your team.

---

## 4. Messaging Framework

### Hero Copy
**Headline:** Consistent AI agents. No black box.
**Sub-headline:** agents-maker gives your LLM pipelines a structured phase
model so every engineer on your team can read, debug, and fix agent behavior
without guessing.

### Proof Points
1. **Open source, MIT licensed** — your logic lives in your repo, not in a
   vendor's cloud
2. **YAML-configured phase routing** — readable by any engineer; reviewable in
   a PR
3. **Claude API integration with prompt caching** — built-in cost control, not
   an afterthought
4. **15-minute HuggingFace demo** — runs in browser, no install required

### Objection Handling
| Objection | Response |
|-----------|----------|
| "We already use LangChain" | agents-maker is the coordination layer above your chains — they compose |
| "Too much to learn right now" | Run the HF demo in 15 min; if it doesn't click, we failed |
| "Why not CrewAI/AutoGen?" | Role-playing agents ≠ phase-structured routing; different guarantee |
| "Is this production-ready?" | 0.4.1-beta — be honest; show the roadmap |

---

## 5. Channel Plan

### GitHub (Owned — T-13)
Rewrite README above-the-fold to match hero copy exactly. Structure:
1. One-line hero headline
2. One-sentence sub-headline
3. `pip install agents-maker` (immediately visible, no scroll)
4. "Why this exists" — 3-paragraph pain narrative in first person
5. 5-minute quickstart with a code review agent example
6. Link to HuggingFace demo prominently in top section

### HuggingFace Spaces (Owned — T-7)
- **Space title:** agents-maker — Predictable multi-agent pipelines in your browser
- **Default example:** Code review agent (3 phases: parse → review → format)
- **Description:** Matches positioning statement; ends with GitHub star CTA
- Add "Deploy to your own Space" button in the UI

### X/Twitter Thread (Distribution — T-0, 10 AM ET)

> **Tweet 1 (hook):**
> "We shipped 3 AI features last year. All 3 had the same production bug:
> nobody could explain why the output changed between runs.
>
> Here's the framework we built to fix that."

> **Tweet 2 (pain):**
> "Incident at 2 AM: the summarization agent that worked perfectly in staging
> was producing 400-word outputs instead of 50-word ones in prod.
> 3 hours of debugging. Root cause: prompt version drift we couldn't see."

> **Tweet 3 (solution):**
> "agents-maker gives every LLM pipeline a phase model.
> Each phase has: a defined input contract, a single agent responsible,
> an output schema it must match.
>
> If it breaks, you know exactly where and why. [diagram image]"

> **Tweet 4 (demo):**
> "Here's a 3-phase code review agent running live in HuggingFace Spaces.
> No install. Try it in 2 minutes. [GIF + link]"

> **Tweet 5 (launch):**
> "We're live on Product Hunt today.
> GitHub: [link] — HF Demo: [link]
> If this solves a problem you've hit, a star takes 4 seconds."

> **Tweet 6 (ask):**
> "What's the most frustrating inconsistency you've hit with an LLM pipeline
> in prod? Genuinely curious — it shapes our roadmap."

### HackerNews Show HN (Seeded — T-0, 9 AM ET)

**Title:**
`Show HN: agents-maker – open-source multi-agent framework for predictable, debuggable LLM pipelines`

**Body:**
```
We built agents-maker after spending too many late nights debugging LLM
pipelines where the output "just changed" and nobody could explain why.

The core idea: every agent pipeline gets a phase model. Each phase has a
defined input contract, a single responsible agent, and an output schema it
must satisfy before the next phase runs. If something breaks, you see exactly
which phase failed and why — not a 2000-token blob of intermediate state.

It's MIT licensed, integrates with the Claude API out of the box (with prompt
caching), and the routing config is plain YAML so any engineer on your team
can read and modify it without touching Python.

HuggingFace demo (runs in browser, no install): [link]
GitHub: [link]

Would love feedback — especially from anyone who's hit the "why did this
change?" problem in a real production system.
```

**Comment strategy:** Founder monitors and replies within 2 hours. Prioritize
technical questions over praise. If challenged on design decisions, explain the
tradeoff honestly — HN respects directness.

**Fallback:** If <30 points at 2 hours post, share link directly to
r/MachineLearning with title: "We open-sourced a structured multi-agent
framework after debugging too many unpredictable LLM pipelines — feedback
welcome"

---

## 6. Launch Timeline

| Day | Action | Owner |
|-----|--------|-------|
| T-14 | Positioning statement approved | Founders |
| T-13 | GitHub README rewrite shipped | Eng |
| T-12 | PyPI description updated | Eng |
| T-10 | README live; all links verified | Eng |
| T-7 | HuggingFace Space polished | Eng |
| T-7 | Demo GIF recorded (60 sec) | Eng |
| T-5 | HN post drafted; peer-reviewed | Founder |
| T-5 | X thread drafted; scheduled | Founder |
| T-3 | PH page submitted with assets | Founder |
| T-1 | 20 DMs sent to genuine connections | Founder |
| T-0 | PH live 12:01 AM PT | — |
| T-0 | HN Show HN posted 9 AM ET | Founder |
| T-0 | X thread posted 10 AM ET | Founder |
| T-0 | All comments monitored all day | Founder |
| T+1 | "What we learned" X thread | Founder |
| T+7 | Star milestone shared | Founder |

---

## 7. Personal Network DM Template

> "Hey [name] — we're launching agents-maker on Product Hunt [day]. It's an
> open-source framework for building LLM pipelines that are actually debuggable
> in prod — something I think you'd find useful given [specific thing you know
> about their work].
>
> If you have 2 minutes: [PH link]. A quick upvote would genuinely help us
> get visibility on launch day.
>
> No worries if not — happy to send you the HN thread or GitHub link instead."

Send to: ≤25 people you have a real relationship with. Do not blast a mailing
list. HN and PH both penalize coordinated voting from new/inactive accounts.

---

## 8. Success Metrics

### Launch Week (T-0 to T+7)

| Metric | Minimum (call it a win) | Target | Stretch |
|--------|------------------------|--------|---------|
| PH upvotes | 150 | 300 | 500+ |
| GitHub stars added | +150 | +300 | +600 |
| HF demo runs | 200 | 500 | 1,000 |
| HN front page | Any appearance | Top 20 | Top 5 |
| X thread impressions | 20K | 50K | 100K+ |

### 30-Day Indicators (leading signals for product-market fit)
- GitHub issues opened by strangers (not contributors): target 20+
- Discord/Slack join requests or community asks: target 50+
- Inbound "can we use this at [company]?" messages: target 5+

---

## 9. What We Are Not Doing

To stay focused with zero budget, the following are explicitly out of scope for
this launch:

- Paid ads (any platform)
- Press outreach (no embargo, no TechCrunch pitch)
- YouTube demo video (too slow to produce; GIF + live demo is sufficient)
- Reddit mass-posting (one targeted post only; more reads as spam)
- LinkedIn (wrong audience for developer tool organic launch)

These may be appropriate for a v1.0 launch with a warmed community. Not now.

---

*Brief prepared by agents-maker multi-agent session. Reviewed and approved for
execution. Owner: founding team. Revision cycle: after launch retrospective.*
