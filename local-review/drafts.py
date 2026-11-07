#!/usr/bin/env python3
"""Compare two drafts by what is said in them: what changed, and which markers are already okayed.

    python3 drafts.py OLD_TRANSCRIPT.json NEW_TRANSCRIPT.json     (prints the changes)

Whisper hears the same words a little differently on each run, so a difference in the text
alone proves nothing. A real cut moves everything after it, so a change only counts when the
timing shifts: matched stretches of words before and after it sit at different offsets. That
filters out the noise, and it also means a swap that takes exactly the same time won't show,
nor will anything purely visual. Markers about those stay visible, because a marker is only
hidden when all of this holds: the reviewer ticked it on the last draft, left no note on it, it is the
same kind and lands at the same spot in the speech, and nothing changed near it. A marker about
a note always shows, whatever its capitals, and one with no kind only matches identical text:
in testing on real drafts, two fixes for notes were hidden because neither they nor the old markers at
those spots had a kind, so "no kind" counted as the same kind.
"""
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

MIN_BLOCK = 4      # shorter matches are chance, in a file full of "the" and "of"
SHIFT = 0.4        # seconds of timing shift that counts as an edit
CLOSE = 0.3        # a marker within this of its old spot is the same marker (word times are good to about 0.1 s here)
NEAR_CHANGE = 4.0  # a marker this close to a change comes back for another look


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


def median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2]


def regions(old, new):
    """Stretches of matching words, each with one offset (new time minus old time)."""
    a_idx = [i for i, w in enumerate(old) if norm(w["w"])]
    b_idx = [j for j, w in enumerate(new) if norm(w["w"])]
    a, b = [norm(old[i]["w"]) for i in a_idx], [norm(new[j]["w"]) for j in b_idx]
    out = []
    for m in SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        if m.size < MIN_BLOCK:
            continue
        i0, i1 = a_idx[m.a], a_idx[m.a + m.size - 1]
        j0, j1 = b_idx[m.b], b_idx[m.b + m.size - 1]
        off = median([new[b_idx[m.b + k]]["s"] - old[a_idx[m.a + k]]["s"] for k in range(m.size)])
        if out and abs(out[-1]["offset"] - off) < SHIFT:   # same timing: whisper noise, not an edit
            r = out[-1]
            n0, n1 = r["n"], m.size
            r.update(i1=i1, j1=j1, n=n0 + n1, offset=(r["offset"] * n0 + off * n1) / (n0 + n1))
        else:
            out.append({"i0": i0, "i1": i1, "j0": j0, "j1": j1, "offset": off, "n": m.size})
    return out


def text_of(words, i0, i1):
    return " ".join(w["w"] for w in words[i0:i1])


def trim_shared(removed, added):
    """Whisper may draw a boundary a word off: words on both sides of a change aren't part of it."""
    r, a = removed.split(), added.split()
    while r and a and norm(r[0]) == norm(a[0]):
        r, a = r[1:], a[1:]
    while r and a and norm(r[-1]) == norm(a[-1]):
        r, a = r[:-1], a[:-1]
    return " ".join(r), " ".join(a)


def changes(old, new, regs):
    """The edits between stretches, in the new draft's time."""
    out = []
    for r0, r1 in zip(regs, regs[1:]):
        removed, added = trim_shared(text_of(old, r0["i1"] + 1, r1["i0"]), text_of(new, r0["j1"] + 1, r1["j0"]))
        had = {norm(w) for w in removed.split()}
        if r1["offset"] < r0["offset"] and all(norm(w) in had for w in added.split()):
            added = ""   # time only went out, so these are words on the cut's edge, not new ones
        out.append({"at": new[r0["j1"] + 1]["s"], "end": new[r1["j0"]]["s"], "shift": round(r1["offset"] - r0["offset"], 2),
                    "removed": removed, "added": added})
    if not regs:
        return out
    # The ends have no stretch beyond them, so compare how much time each draft has out there.
    head_old, head_new = old[regs[0]["i0"]]["s"], new[regs[0]["j0"]]["s"]
    if abs(head_old - head_new) >= SHIFT:
        removed, added = trim_shared(text_of(old, 0, regs[0]["i0"]), text_of(new, 0, regs[0]["j0"]))
        out.insert(0, {"at": 0.0, "end": head_new, "shift": round(head_new - head_old, 2), "removed": removed, "added": added})
    tail_old = old[-1]["e"] - old[regs[-1]["i1"]]["s"]
    tail_new = new[-1]["e"] - new[regs[-1]["j1"]]["s"]
    if abs(tail_old - tail_new) >= SHIFT:
        removed, added = trim_shared(text_of(old, regs[-1]["i1"] + 1, len(old)), text_of(new, regs[-1]["j1"] + 1, len(new)))
        at = new[min(regs[-1]["j1"] + 1, len(new) - 1)]["s"]
        out.append({"at": at, "end": new[-1]["e"], "shift": round(tail_new - tail_old, 2), "removed": removed, "added": added})
    return out


def compare(old_words, new_words):
    regs = regions(old_words, new_words)
    return {"changes": changes(old_words, new_words, regs),
            "map": [{"old": old_words[r["i0"]]["s"], "offset": round(r["offset"], 3)} for r in regs]}


def to_new(t, mapping):
    """Where a moment in the old draft sits in the new one, by the stretch it falls in."""
    off = None
    for m in mapping:
        if m["old"] > t:
            break
        off = m["offset"]
    if off is None:
        off = mapping[0]["offset"] if mapping else 0
    return t + off


def kind_of(text):
    m = re.match(r"[A-Z]{3,}\b", text or "")
    return m.group(0) if m else ""


def same_thing(old, new):
    """Could this be the same marker? Only a real kind, or word for word the same text."""
    a, b = old.get("text") or "", new.get("text") or ""
    if re.match(r"note\b", b, re.I):      # the fix for a note is the thing he asked to see
        return False
    if kind_of(b):
        return kind_of(a) == kind_of(b)
    return " ".join(a.split()) == " ".join(b.split())


def carried(prev, new_markers, cmp, fps):
    """Marker ids in this draft that the reviewer already okayed on the last one."""
    if not prev or not cmp or not prev.get("markers"):
        return {}
    done = set(prev.get("checked") or [])
    notes = prev.get("notes") or []
    def noted(m):
        return any(n.get("marker_id") == m.get("id") or abs(n["frame"] - m["frame"]) <= 3 * fps for n in notes)
    okay = [m for m in prev["markers"] if m.get("id") in done and not noted(m)]
    out = {}
    for m in new_markers:
        if m.get("review"):      # Claude says this one needs eyes whatever came before
            continue
        t = m["frame"] / fps
        if any(c["at"] - NEAR_CHANGE <= t <= c["end"] + NEAR_CHANGE for c in cmp["changes"]):
            continue
        if any(same_thing(o, m) and abs(to_new(o["frame"] / fps, cmp["map"]) - t) <= CLOSE for o in okay):
            out[m["id"]] = prev.get("label") or "the last draft"
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    old, new = (json.loads(Path(p).read_text())["words"] for p in sys.argv[1:])
    cmp = compare(old, new)
    if not cmp["changes"]:
        print("No changes in the speech.")
    for c in cmp["changes"]:
        mins, secs = divmod(c["at"], 60)
        parts = [f'removed "{c["removed"]}"'] if c["removed"] else []
        if c["added"]:
            parts.append(f'added "{c["added"]}"')
        print(f'{int(mins):02}:{secs:05.2f}  {"; ".join(parts) or "pause changed"}  ({c["shift"]:+.2f} s)')


if __name__ == "__main__":
    main()
