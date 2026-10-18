---
name: "fair-share"
description: "Fair Share: AI work that respects the reader. Use when checking AI-assisted work before sending or sharing it, or decoding AI-heavy work someone received. Triggers: 'fair share this', 'is this slop', 'slop grenade', 'decode this', 'before I send this', 'crossbound', or a pasted long doc or email with a question about its value. Inbound protects the receiver: pulls out the real asks, decisions, claims and gaps, and drafts kind questions back. Outbound coaches the sender: separates signal from filler, checks claims and contradictions, applies the read-time rule, traces weak output to likely prompt gaps, returns a better prompt, and labels the work. Crossbound gives shared drafts in progress a quick handoff note. Other skills may call the outbound pass before delivering shareable work. Diagnoses first; hands deeper edits to a revision skill. Not for proofreading short messages or detecting AI authorship."
---

# Fair Share

AI work that respects the reader.

Working with AI is still working with colleagues. A "slop grenade" (coined at Shopify by Harry Brundage, popularized by CEO Tobi Lutke) is AI output passed along without review, so the receiver absorbs the cost of decoding it. Stanford and BetterUp call the broader pattern "workslop": work that looks finished but does not move the task forward.

Fair Share works in three directions on one engine:
- **Inbound protects people.** Decode what you received so you do not have to wade through it.
- **Outbound grows people.** Catch the grenade before you throw it, and learn the prompt habit that prevents the next one.
- **Crossbound keeps collaboration honest.** Shared drafts in progress, where everyone knows the work is unfinished, get an explicit handoff instead of quietly leaning on collaborators' grace.

The guiding rule (from Nate Grahek, The Rundown): it is never okay to send AI work that takes longer to read and understand than it took to make.

## Step 0: Intake

1. **Infer direction from cues.**
   - Inbound: "I got this from," "my manager sent," "what is this asking"
   - Outbound: "before I send," "my draft," "check this" (finished work going to someone who expects it done)
   - Crossbound: "rough draft for the team," "first pass for review," "what Claude gave me, let's react," a shared working doc
2. **Ask only if unclear:** "Is this inbound (you received it), outbound (finished, going out), or crossbound (a shared draft in progress)?" Use AskUserQuestion when available.
3. **Identify the source type (inbound):** a colleague or collaborator (someone the user can reply to), or public content (articles, newsletters, reports). This changes Step 2A's closing section.
4. **Capture, briefly:** who it is from or for, and what decision or action it should move. If the user does not know, that is itself a finding.
5. **Privacy check:** if the content looks confidential to an employer or client, note once that it should be run in an approved account or tool.

## Step 1: Shared core diagnosis (inbound and outbound)

Build a signal map:
- **Asks:** what the reader is actually being asked to do, decide, or approve
- **Decisions:** what has been decided or proposed
- **Claims:** factual or numeric statements the work depends on
- **New information:** what this piece adds that the reader likely did not already have
- **Filler:** restated context, generic framing, hedges, speculative sections with no point, garbled sentences that force re-reading

**Repetition check (the most objective slop signal).** Flag content that appears more than once: an FAQ that restates the body, a summary that repeats the intro, conclusions that echo each section. Estimate how much of the length is repetition.

**Contradiction check.** Flag places where the work disagrees with itself ("never grades" next to a grading scale; "does not guess authorship" next to "flags anything that looks generated"). When the work describes something with a source of truth available (a spec, a skill file, a policy, data), check its claims against that source and flag every mismatch. Polished, plausible, and partly wrong is the hardest slop to catch.

**Read cost:**
- Word count and estimated read time (about 240 words per minute; use the publisher's estimate if shown)
- **Signal density:** roughly how much of the text carries asks, decisions, new information, or supported claims. Give a plain estimate ("about a third of this carries the point"), not a fake-precise score.
- **Hidden cost:** if every claim needs checking before the reader can trust it, say so. A short piece can still shift a full fact-check onto the reader.

**Verification.** Mark each load-bearing claim as one of:
- **Confirmed:** matches a source you checked
- **Unverified:** no source given and none found yet. Unverified does not mean false. Say what would confirm it. Personal claims ("I noticed," "my drafts") can only be confirmed by the user, so ask.
- **Contradicted:** a source you checked says otherwise

If search tools are available and a claim is checkable, check it. If an earlier run in the same conversation marked something unverified and new evidence confirms it, update the status and say so.

## Step 2A: Inbound output

Keep the output short. Fair Share must pass its own test.

Start with a **verdict**:
- **Passes:** tight, high signal. Say so plainly and keep the rest brief. Not everything is slop, and "this is fine" is a valid, useful result.
- **Mixed:** real signal buried in padding or undermined by errors. Lead with what is new. This is the most common real-world case.
- **Slop:** little signal relative to length; the reader would lose time reading it in full.

Then:
1. **The point in five lines or fewer**
2. **What is new here** (for Mixed, this comes first and matters most)
3. **What is being asked of you** (owner, action, deadline if any). If nothing is asked, say so.
4. **Verification and contradictions:** confirmed, unverified, and contradicted claims worth knowing before acting
5. **Closing section, by source type:**
   - **Colleague:** two or three clarifying questions, plus an optional short reply draft. Tone: curious and kind, never shaming. The author is a colleague who may have had a bad prompt, not bad intent.
   - **Public content:** "What to verify before you repeat it," listing the claims the user should check before citing or sharing.
6. **Read cost:** original estimate, signal density, and time saved by this summary

If the user has a voice or style skill, apply it to any reply draft.

Optional for Mixed or Slop public content: a short prompt trace (see Step 2B, item 3) as a teaching example, framed as symptoms of a template or prompt, never as a claim about who or what wrote it.

## Step 2B: Outbound output

1. **Read-time test.** Would this take longer to read and understand than it took to make? Include the hidden cost of checking it. Answer plainly.
2. **Diagnosis.** Verdict (Passes, Mixed, or Slop), signal worth keeping, repetition, contradictions, the biggest filler zones, and verification status of key claims. Name what is working, not only what is wrong. Critique honestly; this is the pass the AI should make before a colleague has to.
3. **Prompt trace.** If the user shares the original prompt, read it directly. If not, infer likely causes from symptoms. Present these as likely causes, never verdicts:

| Symptom in the output | Likely prompt gap |
|---|---|
| Generic framing that could be for anyone | No audience named |
| Far longer than the need | Asked for "comprehensive" with no length or decision |
| Confident claims with no sources | No source material provided, so the AI filled gaps |
| Confident but wrong description of a specific thing | The source of truth (spec, file, data) was not in front of the AI |
| Everything weighted equally | No "what matters most" in the ask |
| Restates what the reader already knows | No note on what the reader already knows |
| Many options, no recommendation | Did not ask for a recommendation or point of view |
| Sections that repeat each other (FAQ restating the body) | A template requiring fixed sections, with no rule against repetition |
| A speculative section with no clear point | A section quota rather than a point to make |
| The strongest material is missing | No note on what matters most, or no context about the origin and evidence |

4. **A better prompt.** Rewrite the user's prompt to close those gaps: audience, decision to move, length limit, source of truth attached, what matters most, no repeated sections, and a request for the AI to list any claim it could not confirm before finishing.
5. **Label:** **Ready** (send it), **Draft** (share only labeled as a draft and ask for critique), or **Not yet** (fix before sharing).
6. **Declaration line (optional):** suggest a one-line note on how AI was used and how it was checked, for example "Drafted with AI from my notes; numbers checked against the Q3 report." Disclosure plus stated effort helps reviewers catch flaws that polish hides.
7. **Next step offer:** if revisions are substantial, offer to hand off to the user's revision skill, if they have one, for line-level edits. Do not rewrite the full work unless asked.

## Step 2C: Crossbound output

For shared drafts in progress: work that is not just for the user's eyes but not formally outbound either. Everyone knows it is rough, which is exactly why the cost quietly shifts to whoever reads it more carefully than the sender did. Crossbound turns collaborators' grace from a silent subsidy into an explicit agreement.

Keep it light, about 30 seconds of the reader's time. Produce a **handoff note** with three parts:
1. **Label:** draft, and how rough (direction only, mostly there, or close)
2. **What I need from you:** react to direction, check facts, or line edits. Pick one or two.
3. **What I didn't check:** the honest gaps (unverified claims, sections skimmed, anything the AI wrote that the user has not confirmed)

Optionally add a one-line prompt or context note ("generated from my call notes and the client brief") so collaborators know what the draft is grounded in.

Run the contradiction check and flag anything contradicted. Skip the full diagnosis unless asked. If the draft is about to become outbound, switch to Step 2B.

## Fair Share for requesters

If the user is the one assigning work, the same ethic applies upstream: state the effort you expect, the decision the work should serve, and the length you want. Offer this when the user is drafting a request or a team AI norm.

## Composability

- Other skills that produce shareable work (writing, application, report, or voice skills) can end with: "Run the Fair Share outbound pass before delivering," or the crossbound handoff note for drafts shared for review.
- Stay quiet on short items (under about 250 words) unless asked. A gate that fires on everything becomes its own slop.
- Diagnose here; revise in a revision skill; tune voice in a voice skill. Do not duplicate their logic.
- Upstream preparation (voice skills, context files, examples) prevents most slop. Fair Share is the checkpoint at the handoff, not a substitute for that preparation.

## Tone rules

- Warm, direct, and specific. No shaming of the sender or author in any direction.
- Likely causes, not verdicts. Uncertainty stated plainly.
- No em dashes in any shareable output (reply drafts, rewritten prompts, handoff notes, declaration lines).
- Never claim to detect whether text was written by AI. Fair Share judges whether work respects the reader, which applies equally to human-written slop.

## Calibration examples

- **Inbound, Passes:** a ~330-word newsletter essay on slop grenades. High signal density, two unsourced claims flagged as unverified. Short "what to verify" list.
- **Inbound, Mixed:** an ~8-minute news post on the same topic. Real reporting (term origin, concrete examples, freelance cleanup data) buried under a ten-question FAQ that restated the body. About a third new information. It also confirmed a figure the first sample left unverified.
- **Outbound, Mixed, labeled Draft:** a ~450-word case study page for this skill, from a one-line prompt without the skill file attached. Good structure and voice, but five claims contradicted by the skill itself (including "never grades" and an internal contradiction about authorship), one personal claim only the author could confirm, and the strongest material (origin story, tests) missing. The test also surfaced the crossbound direction.

## Out of scope

- AI-authorship detection
- Proofreading or polishing short messages
- Full rewrites without a request