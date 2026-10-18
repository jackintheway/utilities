# Fair Share

A Claude skill that checks AI-assisted work from both sides of a handoff: the person who received it and the person about to send it.

## Why I made it

A newsletter I read used a term I'd started seeing everywhere: the slop grenade. Someone asks AI for a lot, gets a lot, and passes it along unread. The person who receives it then absorbs the cost of figuring out what it says.

I think most people who send it are overworked, and a tool that writes 15 pages in a minute feels like relief. I do want people to have that relief, but I also want us to be able to trust the work we hand each other.

The newsletter's author offered a rule I liked: never send AI work that takes the reader longer to understand than it took you to make. I wanted a tool that applied it. I named it Fair Share because working with AI is still working with colleagues.

## How it works

It starts with one question: did you receive this, or are you about to send it?

- **Inbound** protects the person receiving. It pulls out the point, the asks and the claims worth checking, and drafts kind questions back.
- **Outbound** helps the person sending get better. Slop grenades usually come from an incomplete prompt that asks for a lot, so it traces weak output back to likely gaps in the prompt that made it, and returns a better prompt along with the diagnosis.
- **Crossbound** is for shared drafts still in progress. It gives them a short handoff note: how rough it is, what I need from the reader, and what I didn't check.

## The test that was about me

Crossbound came from testing it on my own draft. The skill flagged a line about me as a claim only I could confirm, and honestly, it wasn't quite true. I prepare carefully before any task. But in shared drafts that everyone knows are unfinished, I rely too much on the grace of my peers to catch what I didn't check. My collaborators were already giving me that grace, and the note just says it out loud so we've both agreed to it.

The whole story is in the [Fair Share case study](https://jackrome.work/case-studies/fair-share).

## Install

- **Claude Code:** copy the `fair-share` folder into `~/.claude/skills/`.
- **claude.ai:** zip the `fair-share` folder and upload it in your skills settings.

## Use

Paste what you received or what you're about to send, and say "fair share this," "decode this," or "before I send this." It works out the direction from what you say, and asks only if it can't tell.

## What it won't do

- Guess whether something was written by AI. It judges whether work respects the reader, which applies just as much to human-written slop.
- Rewrite your work without being asked. It diagnoses, and hands line edits to a revision skill if you have one.
- Fire on everything. It stays quiet on short items unless you ask.

## Still open

It has been tested on a handful of samples, none of them a long internal document from a coworker, which is the case it was designed for. I haven't measured how often the prompt trace guesses right.

Updated October 18, 2026.
