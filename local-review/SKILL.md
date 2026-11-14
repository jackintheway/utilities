---
name: local-review
description: "Review a video draft on your Mac, in the browser, with frame-accurate notes and no upload: a Frame.io-style comment loop for when you are the only reviewer and are at your computer. Starts a small local server (127.0.0.1 only) that plays the exported draft with scrubbing, 10 s jumps, frame steps and speed controls, beside a clickable word-timed transcript you can highlight to make a note, and shows only what needs your eyes on a later draft. Claude's 'check here' markers sit on the timeline; your notes save to a JSON file beside the video as you type, which Claude reads and turns into a round of notes. Works for any editing project. Also holds a standing rule: whenever Claude finishes a video edit, it writes these markers before saying the draft is ready, so load this skill at that moment too. Invoke as 'local review', 'open the local reviewer', 'review it locally' or 'review draft N here'. Always trigger this rather than improvising a player: the markers, the notes file and the notes format are the point."
---

# Local review

A review loop without the upload, for drafts only you review. A draft plays from its
exports folder at full quality, you leave notes on exact frames, and Claude reads them
straight from disk.

## Context Setup

Before the first run in a project, ask the user, in one short message, only what the
project's own instructions don't already answer:

- **Is there a cloud review tool for other times?** (Frame.io, Vimeo review, none.) If
  there is, ask at each draft: local reviewer or that tool? The cloud tool is for review
  away from the computer or when anyone else reviews. Never assume last draft's answer.
- **Where do notes go?** The default is described under "Where notes and markers live";
  ask only if the project already keeps notes somewhere.
- **Which marker kinds does the project use?** Defaults: `CHANGE`, `CALL`, `CHECK`,
  `NOTE`. A project may add its own, such as `SWITCH` for camera or slide changes.
- **Should every finished edit get markers automatically?** (Section 1. The default is yes.)

---

## Files

- `server.py`: the local server. Plays the video with Range requests (a 7 GB file seeks
  at once), serves the markers, saves the notes, grabs stills and opens other videos. Binds
  to 127.0.0.1 and refuses requests from any other site, so nothing leaves the computer.
  Python standard library only, and it runs on macOS's own /usr/bin/python3.
- `review.html`: the player. Scrub bar with marker ticks, timecode HH:MM:SS:FF, ±10 s,
  ±1 frame, speeds 0.5× to 3×, the transcript, a marker list to filter and tick off, notes.
  `?` shows the keys.
- `transcribe.py`: the export's own word-timed transcript, with whisper-cli and the
  `ggml-base.en.bin` model (about 30 s for a 45-minute export on a recent Mac). English
  only, and no speaker names. Word times are good to about a second.
- `drafts.py`: compares two drafts' transcripts: what was cut or added, and which markers
  the reviewer already okayed. Claude can run it directly to confirm a cut landed (section 4).
- `notes_to_md.py`: notes JSON → `round-N-notes.md`, a plain table of notes.
- `launch.py`: opens one video in a reviewer: finds where the notes go, reads the frame
  rate and start timecode with ffprobe, starts the server in the background on a free
  port (8765 to 8784) and opens the page. If that video is already open, it reopens it.
- `local-review-app.applescript` and `build_app.sh`: build `Local Reviewer.app`, a Dock app.
  Drop a video on it, or click it and choose one; it runs `launch.py`. Its servers stop
  themselves 15 minutes after the page closes. Log: `~/Library/Logs/local-review.log`.

## Where notes and markers live

`launch.py` decides, so Claude and the app always agree:
- A video in an `exports/` folder with a `notes/` folder beside it: that `notes/` folder.
  Anything else: a `review-notes/` folder next to the video.
- Named for the video, so each version of a draft keeps its own: `<video name>-review.json`
  (the reviewer's notes) and `<video name>-markers.json` (Claude's). A `-premiere` render
  shares its draft's files.
- Beside those: `<video name>-transcript.json`, `<video name>-compare.json` and a
  `<video name>-frames/` folder of grabbed stills.

## 1. Every finished edit gets markers

**A standing rule for the user's video editing, unless they turned it off in Context Setup.**
Whenever Claude finishes an edit the user will look at (a new draft, a re-export after
notes, a small fix), it isn't ready until its markers are written. They let the user go
straight to what needs their eyes instead of hunting for it.

**When.** Once the export exists and Claude has checked it, before saying it's ready.
Markers sit on frames of the exported file, so an edit with no export yet gets them when it
is exported; say so rather than skipping. Write them before asking which review tool. They
become cloud comments only where the project's rules ask for that, and never on a draft a
client can see.

**One marker for each:**
- Anything new or changed in this export. A fix for a note names the note.
- Any call Claude made that the user might make differently.
- Anything Claude couldn't verify from the file, such as how a cut sounds or feels.

A change repeated many times (twenty name cards) gets a marker on the first and on any
risky one, and says how many there are, unless the project asks for every one. A project
that wants to watch every cut of one kind can ask for each to sit 2 s before the cut, so
pressing play shows it happen. The page has one marker list, so start each marker's text
with its kind in capitals (`CHANGE`, `CALL`, `CHECK`, `NOTE 1`). Each marker says what
changed and what to look at, in one plain line.

```json
{"markers": [{"id": "m1", "frame": 6291, "text": "CHANGE: new lower third for the second speaker. Check placement."}]}
```

Ask for the path instead of working it out, so Claude and the app always agree:

```bash
python3 ~/.claude/skills/local-review/launch.py <export.mp4> --paths
```

`frame` is the frame number in the exported file (seconds × fps): the export's own clock,
not a recording's clock or an older cut's. Every marker needs an `id`. The page shows
markers in gold and turns them green as they are ticked.

**Every export gets a fresh list.** A re-cut moves frames, so write the list on the new
export's clock. The page reads it when it loads: if the user already has it open, ask them
to reload.

**Later drafts show only what needs their eyes.** Nobody should scroll past 80 markers they
already okayed to find the 2 that matter. So write the whole list as usual, and the page hides
a marker when all of this holds: it was ticked on the last draft with no note on it, it is
the same kind at the same spot in the speech, and nothing changed within 4 s. A marker with no
kind only matches identical text, and one starting `NOTE` in any capitals always shows. The
page shows "This draft" by default, with "All" one click away, and adds a CUT, ADDED or
CHANGED marker for each change it finds in the speech, 2 s early so playing shows it. Add
`"review": true` to a marker that must show regardless, such as a purely visual change at the
same spot, because the comparison only hears speech.

The last draft is found two ways. A new file `...draft-K...` looks for `draft-(K-1)` beside it.
A re-export under the same name archives the old notes as `<video name>-review-draft-K.json`
by itself when the page's server starts, and they stay complete (ticks, notes, the marker
list), as does the old transcript.

**Make the transcript now,** so the page opens with it ready instead of 30 s later, and so the
words can help place markers:

```bash
python3 ~/.claude/skills/local-review/transcribe.py <export.mp4>
```

**Check before handing over.** Every frame falls inside the file, and a still pulled at each
marker about something visible shows that thing. A marker in the wrong place costs more than
no marker.

**Hand over** with how many markers there are and which one matters most. If nothing truly
needs their eyes, say so plainly rather than leaving an empty list to explain itself.

## 2. Start it

The user can drop the video on **Local Reviewer.app**. When Claude starts it:

```bash
python3 ~/.claude/skills/local-review/launch.py <export.mp4>
```

It prints the page's address and the notes path, and opens the page in the default browser
(`--no-open` to skip that). Give the user the link either way.

To run the server by hand instead (other paths, no idle stop):

```bash
python3 ~/.claude/skills/local-review/server.py \
  --video <export.mp4> --notes <notes.json> --markers <markers.json> \
  --transcript <transcript.json> --fps 25 --title "<project> draft K" --port 8765 [--idle-exit 900]
```

- `--fps` must match the export (25, or 29.97: frames count at 29.97 and the timecode reads
  non-drop at 30, as Premiere shows it). `--start-tc` only if the file's source timecode
  doesn't start at 00:00:00:00, so the clock matches the editing app.
- The server needs to keep running during the review; the page says "NOT SAVED" if it
  stops. With `launch.py` (and the app) it stops itself 15 minutes after the page closes.
- Check it before handing over: `curl -s -o /dev/null -w '%{http_code}' -H 'Range: bytes=0-99' http://127.0.0.1:8765/video`
  should print `206`, and `curl -s http://127.0.0.1:8765/api/markers` should list the markers.

## 3. The review

Space or K plays, J and L jump 10 s, arrows step a frame (Shift: 10 s), `-` and `=`
change speed, `[` and `]` jump between the markers in view, and X ticks the current marker,
jumps to the next unticked one and plays. C or Enter writes a note (it pauses), T shows or
hides the transcript, G grabs the exact frame as a full-size still on a note, and I sets an
In point for a range with no words to highlight. Notes save as the reviewer goes. Nothing
about the review needs Claude while it runs.

- **Transcript:** clicking a word jumps there, and Cmd+F searches. Highlighting words and
  pressing C makes a note on them with its range and exact words. Cuts since the last draft
  show in place with what was removed.
- **Notes come in three types,** switched with Tab while writing: Change (the default), Keep
  (it's working, leave it) and Rule (do this from now on).
- **A note written within 8 s of a marker replies to it,** which means "looked, not fine", the
  opposite of a tick. The ✕ takes the link off, or use Reply on the marker itself.
- **A note on a range can show the cut it asks for.** Try this cut, in the note box, makes
  playback skip the range so the reviewer hears the join; In and Out nudge each edge a frame and
  replay it. Timeline opens a close-up of the sound, three seconds around each edge: drag the cut
  point, or click a view and use the arrows (a frame, Shift 5) and Space, and the picture shows
  the last frame kept or the first kept after. The note still has to say what they want: a cut
  with no words won't save. Every tried cut plays together, so the draft can be watched as it
  would be, and D (or the Cuts button) turns them off and on. It is a demonstration for Claude,
  never an edit: the video and the editing project are untouched, and the browser's skip is good
  to about a frame.
- **A note can show a picture switch too, when the export has a sources file.** Try a switch
  lays another raw picture over a stretch, in step with the export, so the reviewer sees the
  switch happen. On a single frame it runs to the next switch already in the cut; on a range it
  covers the range; it picks the picture that is up least there, and the reviewer can pick
  another. Same nudges, timeline, words rule and D toggle as a cut, and one note can carry both.
  Whatever is baked into the export at that spot (a title, a logo) is hidden under it. Without
  the file the button isn't there; see "The sources file" below.
- **Open another** lists the videos in this folder, or chooses any file, each in its own tab.

### The sources file

Claude writes it, from the editing project the export came from, as
`<notes folder>/<video name>-sources.json`. How to read a project is up to the project, so no
writer ships here. The shape:

```
{"pictures": [{"name": "Camera A", "path": "/full/path/to/raw-a.mp4"},
              {"name": "Camera B", "path": "/full/path/to/raw-b.mp4"}],
 "map": [{"export": s, "end": s, "recording": s}, ...],
 "up":  [{"at": s, "end": s, "picture": "Camera A"}, ...]}
```

`pictures` are the raw recordings, which must share one clock. `map` takes each stretch of the
export (from `export` to `end`, in seconds) back to the recording's clock, where it starts at
`recording`. `up` says which picture the export shows when. Fewer than two pictures that exist
on disk, or no map, and switches stay off.

## 4. Pull the notes

When the user says they're done ("pull the notes"):

```bash
python3 ~/.claude/skills/local-review/notes_to_md.py <notes>/<video name>-review.json \
  <notes>/round-N-notes.md --round N --draft K --markers <notes>/<video name>-markers.json
```

Then map the notes onto the edit, the way the project handles any round of notes. A note may
carry the words highlighted, the marker it replies to and a still's path, and they come
through in its text. A demonstrated cut comes through as exact frames on the export's clock
(`in` is the first frame removed, `out` the first kept after): the reviewer heard that join, so
make the cut on those frames, mapped to the recording's clock, rather than re-deciding the edges
from the words. A demonstrated switch names its picture and frames the same way, and carries the
recording's clock too (`rec_in`, `rec_out`, in seconds). Keep notes ask for no change, so don't touch those moments. Rule notes
get their own list: file them in the project's rules, and say where. Ticked markers are
listed under the table: ticked means "looked, fine", and an unticked one is worth asking about.

After a fix, confirm a cut landed, for instance that a word the user asked to remove is gone,
by comparing the two transcripts. It only sees speech whose timing changed, so check anything
else in the file itself:

```bash
python3 ~/.claude/skills/local-review/drafts.py <old>-transcript.json <new>-transcript.json
```

A server started by hand needs stopping when the review is over; one from `launch.py` stops
itself. Nothing to resolve: notes are marked fixed in the notes file only.

## Rules

- **Local only.** 127.0.0.1, no tunnels, no uploads, no sharing. If someone else needs to see
  a draft, use a review tool built for that.
- **The notes JSON belongs to the reviewer.** Claude reads it and never rewrites their notes;
  new notes for a later draft go in a new round file. Archiving a re-export's notes under a
  new name leaves their contents alone.
- **The video is read only.** The server only reads the export. Transcripts and stills go in
  the notes folder.
