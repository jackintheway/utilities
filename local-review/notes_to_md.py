#!/usr/bin/env python3
"""Turn a local review's notes file into the round-N notes markdown.

    python3 notes_to_md.py NOTES.json OUT.md --round 2 --draft 4 [--deliverable "playback"]

A plain table a project's revision step can read, the same shape as a Frame.io notes round.
Comment ids are the local note ids; "Pinned" is the frame the reviewer noted on, "Typed" any time they
wrote in the text (flagged when they disagree by more than 2 s). The note text carries the
words he highlighted, the marker he replied to, any still he grabbed and any cut he
demonstrated (its exact frames: he tried it in the player and heard the join). Keep and Rule notes
also get their own lists: a Keep asks for no change, and a Rule belongs in the project's rules
not just this round. Claude's markers the reviewer ticked are listed below the
table, since a checked marker means "looked, fine".
"""
import argparse
import json
import re
from pathlib import Path

TYPED = re.compile(r"\b(?:(\d{1,2}):)?(\d{1,2}):(\d{2})(?::(\d{2}))?\b")
STATUS = {"keep": "keep, no change", "rule": "file as a rule"}


def frames_from(tc, fps):
    h, m, s, f = (int(x) for x in tc.split(":"))
    return ((h * 60 + m) * 60 + s) * round(fps) + f


def clean(s):
    return s.replace("|", "\\|").replace("\n", " / ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("notes")
    ap.add_argument("out")
    ap.add_argument("--round", required=True)
    ap.add_argument("--draft", required=True)
    ap.add_argument("--deliverable", default="")
    ap.add_argument("--markers")
    a = ap.parse_args()
    d = json.loads(Path(a.notes).read_text())
    fps = d.get("fps", 25)
    names = {m.get("id"): m for m in d.get("markers_seen") or []}
    if a.markers and Path(a.markers).exists():
        names.update({m.get("id"): m for m in json.loads(Path(a.markers).read_text()).get("markers", [])})
    rows, keeps, rules = [], [], []
    for i, n in enumerate(sorted(d["notes"], key=lambda n: n["frame"]), 1):
        pinned = n["tc"] + (f" to {n['end_tc']}" if n.get("end_tc") else "")
        typed, flag = "", ""
        m = TYPED.search(n["text"])
        if m:
            typed = m.group(0)
            h, mi, s = int(m.group(1) or 0), int(m.group(2)), int(m.group(3))
            secs = h * 3600 + mi * 60 + s
            off = abs(secs - n["frame"] / fps)
            if off > 2:
                flag = f"pinned and typed differ by {off:.0f} s"
        parts = []
        if n.get("marker_id"):
            target = names.get(n["marker_id"])
            parts.append(f"Reply to {n['marker_id']}" + (f" ({target['text']})" if target else "") + ":")
        if n.get("quote"):
            parts.append(f"On the words \"{n['quote']}\":")
        if n["text"]:
            parts.append(n["text"])
        c = n.get("cut")
        if c:
            parts.append(f"Demonstrated cut: {c['in_tc']} to {c['out_tc']} on the export's clock, frames {c['in']} up to but not "
                         f"including {c['out']} ({c['out'] - c['in']} frames, {(c['out'] - c['in']) / fps:.2f} s).")
        sw = n.get("switch")
        if sw:
            rec = (f" Recording clock: {sw['rec_in']:.2f} s to {sw['rec_out']:.2f} s." if sw.get("rec_in") is not None and sw.get("rec_out") is not None else "")
            parts.append(f"Demonstrated switch: {sw['to']} up from {sw['in_tc']} to {sw['out_tc']} on the export's clock, frames {sw['in']} up to "
                         f"but not including {sw['out']} ({sw['out'] - sw['in']} frames, {(sw['out'] - sw['in']) / fps:.2f} s).{rec}")
        if n.get("image"):
            parts.append(f"Still: {n['image']}")
        text = clean(" ".join(parts))
        kind = n.get("kind")
        rows.append(f"| {i} | {n['id']} | {a.draft} | {pinned} | {typed or '-'} | {text} | {flag or '-'} | {STATUS.get(kind, 'open')} |")
        if kind == "keep":
            keeps.append(f"- {pinned}: {text}")
        elif kind == "rule":
            rules.append(f"- {pinned}: {text}")
    title = f"# Round {a.round} notes: {a.deliverable + ', ' if a.deliverable else ''}draft {a.draft}"
    out = [title, "", f"Source: local review of {Path(d['video']).name} (saved {d.get('updated', '?')})", "",
           "| # | Comment id | Draft | Pinned | Typed | Note | Flag | Status |",
           "|---|---|---|---|---|---|---|---|"] + rows
    if not rows:
        out.append("| - | - | - | - | - | No notes | - | - |")
    if rules:
        out += ["", "## Rules to follow from now on", "", "File these in the project's rules, not just this round.", ""] + rules
    if keeps:
        out += ["", "## What's working: keep", ""] + keeps
    checked = d.get("markers_checked") or []
    if checked:
        out += ["", "## Claude's markers that were checked", ""]
        for mid in checked:
            m = names.get(mid)
            out.append(f"- {mid}" + (f": {m['text']}" if m else ""))
    Path(a.out).write_text("\n".join(out) + "\n")
    print(f"Wrote {a.out}: {len(rows)} note(s), {len(checked)} marker(s) checked")


if __name__ == "__main__":
    main()
