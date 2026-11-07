# Local Reviewer

A small app that runs on your Mac for reviewing video drafts with Claude Code: notes on exact frames, a transcript beside the video, and markers from the assistant that made the cut.

## Why I made it

I've been editing video for 15 years. My review loop for my own drafts used to run through Frame.io: export, upload, wait, then pin comments for the assistant to pull. With a client that's the right tool. But a lot of the time I'm the only reviewer, sitting at the same Mac the draft was exported on.

So I asked Claude Code for something that lets me comment at any point and gives the assistant the timestamps the same way Frame.io does. It takes the parts I love from the tools I use: a transcript next to playback like Riverside and Descript, timestamped comments like Frame.io, and in and out points like Premiere.

It doesn't edit, and for now that's on purpose. Because I can't change the cut from inside it, I have to put into words exactly what I want, and on several edits that took a cut from an A- to an A+.

## What it does

- Plays your export straight from its folder, with timecode to the frame, frame steps, 10-second jumps and speeds from 0.5× to 3×.
- Saves every note as you type, into a file beside the video that Claude reads. Nothing is uploaded.
- Shows a word-timed transcript beside the video. Click a word to jump there, or highlight words and press C to make a note on them.
- Shows Claude's markers on everything it changed, every call it made and anything it couldn't check from the file. X ticks one and plays the next.
- On a later draft, hides the markers you already okayed, and marks every cut it hears in the speech.
- Notes can be a Change, a Keep (leave this alone) or a Rule (do this from now on), and G grabs the exact frame as a full-size still.

The whole story is in the [Local Reviewer case study](https://jackrome.work/case-studies/local-reviewer).

## Install

You need a Mac, Claude Code, and two free tools from [Homebrew](https://brew.sh):

```bash
brew install ffmpeg whisper-cpp
```

Then the speech model whisper uses, about 150 MB:

```bash
mkdir -p ~/.cache/local-review && curl -L -o ~/.cache/local-review/ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
```

Copy the `local-review` folder into `~/.claude/skills/`. If you'd like a Dock app you can drop videos on, run `./build_app.sh` inside that folder and drag `Local Reviewer.app` to your Dock.

## Use

When Claude finishes an edit, it writes its markers and tells you the draft is ready. Say "local review" and it opens the draft in your browser, or drop the video on the Dock app yourself. Press `?` on the page for the keys. When you're done, say "pull the notes" and Claude turns them into a round of notes and gets to work.

The first time you open a video, the transcript takes about 30 seconds for 45 minutes of video while the page is already playing.

## What it won't do

- Edit. Cuts still happen in your editing app.
- Leave your computer. It only answers on 127.0.0.1, and a review with anyone else belongs in a tool built for that.
- Hear anything but English, or tell speakers apart.
- Notice a change that is only in the picture. Claude flags those itself.

## Credit

The ideas are borrowed from tools I love: Frame.io for frame comments, Riverside and Descript for a transcript beside playback, and Premiere for in and out points. Transcription is [whisper.cpp](https://github.com/ggerganov/whisper.cpp).

Updated 2026-11-07
