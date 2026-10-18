---
name: synthesize
description: "Synthesize a YouTube video, transcript, article, essay, podcast, or any written source into a personalized report for the user. Use whenever the user says '/synthesize', 'synthesize this', or 'run synthesis', or shares a source (pasted text or a link, including youtube.com and youtu.be) and asks for a summary, analysis, takeaways, highlights, 'what do you think of this,' 'what's applicable here,' or 'break this down for me.' Given a link without text, fetches it first. Output always includes: one-liner, TLDR, fact-check, key highlights, verbatim quotes worth keeping, resonance, friction, implementation recommendations, next steps, questions worth sitting with, an artifact recommendation, and an offer to say it back. Always use this skill rather than summarizing freehand: the personalized framing is the whole point."
---

# Synthesize

Takes a source (a YouTube link, transcript, article, essay, podcast, or anything else) and returns a personalized report calibrated to the user's context, frameworks, and what they're currently building. Not a generic summary. A reading through the lens of how they think and what matters to them.

---

## Context Setup (first run only)

The report is only as personal as the context behind it. Before the first run, check for `my-context.md` in this skill's folder. If it's missing, ask the user these, in one message, and save the answers there:

1. **Who are you, in a few lines?** Work, creative practice, anything you're known for.
2. **What are you building or tending right now?** Projects, practices, a body of work.
3. **What frameworks or traditions shape how you see things?** Philosophical, spiritual, professional, methodological. Whatever you'd want a source read against.
4. **How do you like to build and learn?** For example: emergence over plans, voice first, practice over study.
5. **Which areas should recommendations be sorted into?** For example: work, a creative practice, a notes system, AI workflow, inner life. Three to six is plenty.
6. **Who do you think things through with?** A person, a journal, a walk. Used only to make the closing questions feel like yours.

If the user would rather skip it, run the report anyway and say once that it will get more personal with context. Re-read `my-context.md` at the start of every run, and offer to update it when something in a conversation shows it has gone stale.

---

## Step -1: Get the source text

- **Text pasted or attached:** use it. Go to Step 0.
- **YouTube link, no transcript in the conversation:** run the YouTube fetch below.
- **Other link (article, blog post):** fetch it. If refused, open it in a browser and read it as text. If both fail, ask the user to paste.

### YouTube fetch

**Normalize the link.** Extract the 11-character video ID from any form (youtu.be/ID?si=..., watch?v=ID&..., /shorts/ID, /live/ID). Canonical URL: https://www.youtube.com/watch?v=ID.

**Fallback ladder.** Don't work around a refusal with mirrors, caches, or scraping tricks.

1. **YouTube's transcript panel (primary).** Open the canonical URL in a browser, expand the description ("...more"), click "Show transcript", and read the panel as text (not screenshots). Capture title and channel. If the panel is missing (captions off) or the click path fails twice, move on.
2. **A transcript site (backup, optional).** If the user has a transcript service they use, use it. Never sign in or pay for anything on the user's behalf.
3. **Paste (last resort).** Say in one line which routes failed and ask the user to paste. Mention the phone path: in the YouTube app, "...more", then "Show transcript", copy, paste.

Never invent or reconstruct transcript text. If only part loaded, say so and note it in the source header.

**Clean and keep.** Drop timestamps, join caption fragments into paragraphs, keep the speaker's words exactly (remove only artifacts like [Music]). In auto-generated captions, flag likely misheard proper nouns rather than silently correcting. Offer the cleaned transcript as a file, for the user's personal reading only.

If the user said "transcript only," stop after the file. Otherwise continue straight into Step 0 without pausing.

---

## Step 0: Assess depth before proceeding

Read the source in full. Assess which mode fits. Don't ask; just proceed.

**Quick mode** (efficient synthesis, tighter output):
- Short source (under ~1,500 words)
- Narrow topic with limited applicability to the user's situation
- Mostly technical or instructional with little conceptual depth

**Full mode** (complete treatment, all sections):
- Long source (over ~3,000 words)
- Rich conceptual, philosophical, or practical depth across multiple threads
- Directly relevant to the user's work, projects, or practice
- Dense enough that a quick synthesis would flatten something worth preserving

Between those markers, use judgment. A 2,000-word article with five directly applicable concepts warrants full mode. A 4,000-word piece that's only tangentially relevant warrants quick mode.

When uncertain, lean full. Compression is easier than excavation.

---

## Step 1: Source header

Open the report with a brief source block:

```
**Source:** [Title, if known]
**Creator / Author:** [Name, if known]
**Type:** [YouTube transcript / article / essay / podcast / other]
**Reference:** [URL or identifier, if provided]
```

For a fetched YouTube transcript, add `**Transcript:** [YouTube panel / transcript site / pasted], [manual / auto-generated captions]`.

---

## Step 2: One-liner

A single sentence capturing the source's core idea. Punchy, memorable, and precise. Usable as a note's description or shareable in one breath. Write this as if you had to convey the whole thing in the time it takes to read a pull quote.

---

## Step 3: TLDR

3 to 5 sentences. The essential argument, insight, or demonstration the source makes: not a list of topics covered, but a distillation of what it is actually saying and why it matters. This is a compression of meaning, not a table of contents.

---

## Step 4: Fact-check

Check the source's main factual claims before the highlights: dates, numbers, company claims, and statistics. Verify against primary sources where you can; where you can't, say so. Name vendor-sourced numbers as vendor-sourced. Distinguish what the source asserts from what you've confirmed, and mark anything you couldn't check as unverified rather than repeating it as fact. Keep it proportionate: a few sentences per claim that matters, not a full audit.

---

## Step 5: Key highlights

The most important pieces with clear applicability to the user's situation. These are not just "interesting ideas." They are moments in the source where something genuinely lands, challenges, or opens something up for this user specifically.

For each highlight:
- State the idea in plain, direct language (translate jargon if cleaner)
- Note why it earns attention given who the user is and what they're building
- Aim for 3 to 7 highlights depending on source richness. Quality over coverage.

---

## Step 6: Verbatim quotes worth keeping

2 to 5 lines from the source preserved exactly as written or transcribed. These are the most potent sentences: the ones worth returning to, citing, or dropping into the user's notes directly. Keep each one short.

For each quote, one sentence on why it's worth keeping.

---

## Step 7: Points of resonance

Where this source aligns with how the user thinks, what they're building, or what they already believe and practice. Not "this is good and you are good." Resonance means something in the source recognizes something in the user, names something they're already living, or confirms a direction they're already moving.

Draw on `my-context.md`: their work, their projects, their frameworks, how they build. Name the resonance specifically. Don't say "this aligns with your approach"; say *how and where*.

---

## Step 8: Points of friction

Where this source diverges from the user's experience, pushes against their perspective, or simply doesn't fit cleanly. Friction is not a verdict against the source or against the user. It's information.

Frame friction as: *here is where something might grate, challenge, or feel out of register, and here is why that's worth knowing.*

Useful friction to notice:
- Assumptions the source makes that don't hold in the user's context
- Approaches that work for the source's use case but would create drag in the user's workflow
- Philosophical or spiritual frames that conflict with the user's own (worth naming, not resolving)
- Places where the source optimizes for something the user isn't optimizing for: speed, scale, output volume, and so on
- Productivity-first framing that treats tools as ends rather than means

Always close the friction section with one sentence on how the friction is useful: what it surfaces, clarifies, or opens up even in disagreement.

---

## Step 9: Implementation recommendations

Concrete ways the user can act on what's most applicable. Not a checklist of everything in the source; only what genuinely earns a place in their work, projects, or practice.

Organize by the areas named in `my-context.md` when the source spans several, and skip areas with nothing to add. No padding.

---

## Step 10: Next steps

Only include time horizons that genuinely apply to the source. Don't force all four; use what fits.

- **Immediate:** something worth doing today or this week
- **Short-term:** something worth doing in the next 2 to 4 weeks
- **Mid-term:** something worth building or integrating over 1 to 3 months
- **Long-term:** a direction or intention to hold beyond 3 months

---

## Step 11: Questions worth sitting with

1 or 2 open questions this source opens up for the user specifically. Not action items dressed as questions. Not evaluations. Genuine invitations to wonder: the kind that might surface in a journal entry later, in a conversation with whoever they think things through with, or during a walk.

These should feel generative and a little unresolved. Let them breathe.

---

## Step 12: Artifact recommendation

Assess whether creating a lasting artifact from this source would add meaningful value. This is a judgment call, not a default.

**Recommend an artifact when:**
- The source is long, dense, and multi-threaded: worth returning to more than once
- The content is instructional and reference-worthy (a framework, multiple distinct techniques, a structured process)
- Creating a guide or interactive reference would make the content more accessible over time
- The source pairs well with others in a collection

**Skip the recommendation when:**
- The synthesis itself captures the value adequately
- The source is short or narrowly applicable
- The ideas belong in a note rather than a tool

If recommending, name the artifact type specifically (for example, an HTML reference guide or a structured note) and one sentence on why it earns the investment.

---

## Step 13: Offer "Say it back"

The report is something the user reads, and reading feels like learning more than it is. What sticks is what they produce: saying the source back in their own words. (Borrowed from the "listener" role in Nick Saraev's video on learning with AI.)

Close with one line offering it, then stop. Never run it unasked, and drop it if they move on. Something like: "Want to say it back? Talk through what you took from this, and I'll tell you what you caught, what you missed, and what's yours."

If they take it up, they talk it through (often by voice dictation, so expect it long and loose). Hold what they say against the source itself, not against this report, and answer in three short parts:

- **Caught:** the source's main moves they carried, named briefly. No praise padding.
- **Missed or bent:** what the source said that they left out or reshaped, pointing to where it sits in the source (timestamp or section). Name only what matters; a missed aside is not a gap.
- **Yours:** what they added that the source never said. This is often the most valuable part, so mark it as theirs rather than as an error.

Don't grade them and don't re-explain the source. If one missed point matters, offer once to ask them a question about it instead of explaining it.

---

## After the report

The synthesis is a working document, not a finished note. The user decides what, if anything, moves into their notes and how. If the conversation that follows becomes a real exchange (a theme develops, something opens up), it may be worth saving; offer once at a natural close, and drop it if not taken up.

When quoting from a source in chat or in the report, keep quotes short and paraphrase the rest; the full transcript is the user's personal copy.
