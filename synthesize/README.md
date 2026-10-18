# Synthesize

A Claude skill that reads a video, article, essay or podcast for what it means to you, not just what it says.

## Why I made it

A summary tells me what a source covers. I wanted to know where it resonates with my outlook and my experience, where the friction is, and how either one is useful for awareness, growth and learning. So I asked for a report that always carries both: the points of resonance and the points of friction, along with a one-line takeaway, a short TLDR, highlights, quotes worth keeping, what to do with it, and a couple of questions worth sitting with.

## How I use it

I don't watch or read much from start to finish. I take in just enough to see there's value, and then I bring it to Claude and run synthesize as a filter, so we can act on what's useful.

The friction section is often the part I learn the most from. And the questions at the end have a way of opening things up. After I synthesized a guide to customizing Claude Code, one question asked what my work would look like from the inside instead of from above. My answer was that "it would look like tending to land, like watering plants, planting seeds," and that has guided how my setup looks and feels since.

## A run that earned its keep

A video I synthesized described how Anthropic's Claude Code team works: give the model a clear definition of done and let it find the route. That's how I briefed Claude for the morning audio episode I wrote about in [Lay of the Land](https://jackrome.work/case-studies/lay-of-the-land), one of my case studies.

## Say it back

The newest step came from [Graft](../graft/). Grafting a video about learning with AI showed that synthesize handed me something to read and never asked me to produce anything, and producing is where learning actually sticks. So now, after the report, synthesize offers to let me say the source back in my own words. It tells me what I caught, what I missed or bent, and what's mine: the part I added that the source never said. It only offers once, and never runs unasked.

## What it does

1. Gets the text: pasted, fetched from a link, or read from a YouTube transcript panel.
2. Decides between a quick and a full report, based on length and depth.
3. Writes the report: source header, one-liner, TLDR, fact-check, highlights, verbatim quotes, resonance, friction, recommendations, next steps, questions worth sitting with, and whether a lasting artifact is worth making.
4. Offers "Say it back."

## Install

- **Claude Code:** copy the `synthesize` folder into `~/.claude/skills/`.
- **claude.ai:** zip the `synthesize` folder and upload it in your skills settings.

The first time it runs, it asks a few questions about you (your work, what you're building, the frameworks you read through, how you like to learn) and saves them as `my-context.md` beside the skill. That file is what makes the report yours. Keep it current.

## Use

Share a source and say "synthesize this." A link alone is fine.

## What it won't do

- Invent or reconstruct a transcript. If only part of one loads, it says so.
- Repeat a claim as fact without checking it. Anything it couldn't verify is marked unverified.
- Turn friction into a verdict, against the source or against you.
- Run "Say it back" unless you take it up.

## Works with

[Graft](../graft/). Synthesize asks what a source means for you; graft asks what, if anything, should change in your setup. I often run one and then the other on the same source.

Updated October 18, 2026.
