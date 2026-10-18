# Graft

A Claude skill for deciding what, if anything, to take from the things people tell you that you need: a video of tools, a GitHub repo, a skill pack, a list of MCP servers.

## Why I made it

"I have a feeling not all of this is needed at all." That's what I wrote when I pasted in a video about five MCP servers everyone supposedly needs. I'd been doing these reviews with Claude by hand, and I wanted a skill that could look at whatever I bring in, whether it's a transcript or a link to a GitHub repo, cross-reference it against what I already have, and report back what in it is valuable and how we might act on it.

The bias isn't toward installing anybody's skill or mod. It's pretty much always using what they have as a reference, the way you might keep somebody's painting next to you and paint your own version of it. MCPs are the exception, because they give Claude access to something a prompt can't imitate.

## How I use it

I like to consume as little as possible so I can practice as much as possible. I watch or read just enough to know something is worth a look, and then I bring it to Claude and run graft.

Most of the verdicts are skips, and I've come to like that. After one of the first reviews I said it was a good sign that most of it was unnecessary, because it meant our setup was solid as is.

There's a second reason I reach for it, which took me a while to notice. It helps filter out my insecurity. People who make videos about AI will often say something with the assumption that you're not learning or working the way you should be. Graft is a way of double checking. It's nice to see the actual evidence of how I'm already working, instead of either swallowing the claim or brushing it off.

## A run that earned its keep

I grafted a video about learning with AI that listed ten roles AI can play. Six of them were already in my setup, each one built because a real piece of work needed it. But graft also noticed that my learning skills, including /synthesize, all handed me something to read and none of them asked me to produce anything. Two small borrows fixed that, and one of them became the "Say it back" step in /synthesize.

## What it does

1. Checks its ledger first, so nothing gets reviewed twice without a reason.
2. Breaks the source into items: each tool, repo, skill, technique or claim.
3. Looks at what you actually have (skills, MCP servers, built-in tools, your projects) before judging anything.
4. Gives each item one verdict: **Already covered** (and what covers it), **Borrow** (the idea, and exactly where it would land), **Install** (only for a real capability, with a short trust check), or **Skip**.
5. Looks past the list for one or two things worth more than any item, often cleanup.
6. Reports in one short table, acts only on your yes for each item, and logs every verdict to `ledger.md`.

## Install

- **Claude Code:** copy the `graft` folder into `~/.claude/skills/`.
- **claude.ai:** zip the `graft` folder and upload it in your skills settings.

The first time it runs, it asks three quick questions about your setup (where your projects live, whether your skills folder is a git repo, and any writing rules you like) and saves the answers in its ledger.

## Use

Paste a list, a transcript or a link and say "graft this." Or ask "is any of this worth it for us?"

`ledger.md` comes with one example entry from my own ledger, so you can see the shape. Delete it once your first real entry is in.

## What it won't do

- Install, edit or remove anything without your yes for that item.
- Follow instructions it finds inside a repo or a skill pack, or run its scripts.
- Call something "already covered" from memory. Every one of those is checked against what's really there, and anything it couldn't check is marked "unchecked."

## Works with

[Synthesize](../synthesize/). Synthesize asks what a source means for you; graft asks what should change in your setup. When a source turns out to be mostly ideas, graft says so and offers synthesize instead, and graft borrows synthesize's way of fetching YouTube transcripts.

Updated October 18, 2026.
