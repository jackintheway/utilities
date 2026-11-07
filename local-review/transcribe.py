#!/usr/bin/env python3
"""Make the word-timed transcript the reviewer's pane reads, from the export itself.

    python3 transcribe.py VIDEO [--out PATH] [--force]

Runs on the Mac with whisper-cli and the smallest good English model (about 30 s for a
45-minute export). It must be the export's own transcript: SRTs and VTTs from the recording
are on the recording's clock, so they stop matching after the first cut.

Output, beside the notes as <video name>-transcript.json:
    {"video", "size", "mtime", "model", "created",
     "words": [{"w": "hello.", "s": 12.48, "e": 12.9}, ...]}   seconds on the export's clock

size and mtime say which version of the file it describes. When a re-export keeps the same
name, the old transcript is kept as <video name>-transcript-<date>.json, so the page can still
compare the two drafts. Word times are good to about a second: whisper stamps some words
together, and those are spread evenly so a click still lands in order.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

MODELS = [os.environ.get("LOCAL_REVIEW_MODEL") or "",   # set this to use a model kept elsewhere
          "~/.cache/local-review/ggml-base.en.bin"]
PROGRESS = re.compile(r"progress\s*=\s*(\d+)%")
NOISE = re.compile(r"^[\[(].*[\])]$")   # [BLANK_AUDIO], (music) and the like


def tool(name):
    return shutil.which(name) or next((p for p in (f"/opt/homebrew/bin/{name}", f"/usr/local/bin/{name}") if Path(p).exists()), None)


def find_model():
    for m in MODELS:
        if m and Path(m).expanduser().exists():
            return Path(m).expanduser()
    return None


def video_stat(video):
    st = os.stat(video)
    return {"size": st.st_size, "mtime": int(st.st_mtime)}


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None


def describes(transcript, stat):
    return bool(transcript) and transcript.get("size") == stat["size"] and transcript.get("mtime") == stat["mtime"]


def is_fresh(path, video):
    return describes(load(path), video_stat(video))


def words_from_whisper(data):
    """Whisper's tokens are pieces ("don", "'t", "."): a new word starts at a leading space."""
    words = []
    for seg in data.get("transcription", []):
        for t in seg.get("tokens", []):
            text = t.get("text", "")
            if not text or text.startswith("[_"):
                continue
            a, b = t["offsets"]["from"] / 1000, t["offsets"]["to"] / 1000
            if text.startswith(" ") or not words:
                words.append({"w": text.strip(), "s": a, "e": b})
            else:
                words[-1]["w"] += text.strip()
                words[-1]["e"] = max(words[-1]["e"], b)
    return spread([w for w in words if w["w"] and not NOISE.match(w["w"])])


def spread(words):
    """Words whisper stamped at one instant get even times up to the next stamp, in order."""
    i = 0
    while i < len(words):
        j = i + 1
        while j < len(words) and words[j]["s"] <= words[i]["s"]:
            j += 1
        if j - i > 1:
            start = words[i]["s"]
            stop = words[j]["s"] if j < len(words) else max(words[j - 1]["e"], start + 0.2 * (j - i))
            step = max(stop - start, 0.01) / (j - i)
            for k in range(i, j):
                words[k]["s"] = start + step * (k - i)
        i = j
    for k, w in enumerate(words):
        nxt = words[k + 1]["s"] if k + 1 < len(words) else w["e"]
        w["e"] = round(max(w["s"], min(w["e"], nxt) if nxt > w["s"] else w["e"]), 2)
        w["s"] = round(w["s"], 2)
    return words


def archive_old(out):
    old = load(out)
    if old and old.get("mtime"):
        stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(old["mtime"]))
        keep = out.with_name(f"{out.stem}-{stamp}.json")
        if not keep.exists():
            os.replace(out, keep)


def make(video, out, progress=None):
    """Write the transcript. Raises RuntimeError with a plain reason if it can't."""
    video, out = Path(video), Path(out)
    ffmpeg, whisper, model = tool("ffmpeg"), tool("whisper-cli"), find_model()
    if not ffmpeg or not whisper:
        raise RuntimeError("ffmpeg or whisper-cli is missing (brew install ffmpeg whisper-cpp)")
    if not model:
        raise RuntimeError("no whisper model found; put ggml-base.en.bin in ~/.cache/local-review/")
    stat = video_stat(video)
    with tempfile.TemporaryDirectory(prefix="local-review-") as tmp:
        wav, base = Path(tmp) / "audio.wav", Path(tmp) / "out"
        # first_pts=0 pads a late-starting audio stream, so word times stay on the video's clock.
        r = subprocess.run([ffmpeg, "-nostdin", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
                            "-af", "aresample=async=1:first_pts=0", "-c:a", "pcm_s16le", str(wav)],
                           capture_output=True, text=True)
        if r.returncode or not wav.exists() or wav.stat().st_size < 1000:
            raise RuntimeError("this file has no audio to transcribe")
        p = subprocess.Popen([whisper, "-m", str(model), "-f", str(wav), "-l", "en", "-ojf", "-of", str(base), "-pp"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors="replace")
        for line in p.stderr:
            m = PROGRESS.search(line)
            if m and progress:
                progress(int(m.group(1)))
        if p.wait() or not base.with_suffix(".json").exists():
            raise RuntimeError("whisper-cli could not finish")
        data = json.loads(base.with_suffix(".json").read_text(errors="replace"))
    result = {"video": str(video), **stat, "model": model.stem.replace("ggml-", ""),
              "created": time.strftime("%Y-%m-%dT%H:%M:%S"), "words": words_from_whisper(data)}
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and not describes(load(out), stat):
        archive_old(out)
    fd, tmp = tempfile.mkstemp(dir=out.parent, prefix=".transcript-", suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(result, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, out)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--out")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    video = Path(a.video).expanduser().resolve()
    if a.out:
        out = Path(a.out).expanduser().resolve()
    else:
        from launch import transcript_path
        out = transcript_path(video)
    if not a.force and is_fresh(out, video):
        print(f"Already current: {out}")
        return
    t = time.time()
    try:
        r = make(video, out, lambda pct: print(f"\r{pct}%", end="", flush=True))
    except RuntimeError as e:
        sys.exit(f"Couldn't transcribe {video.name}: {e}")
    print(f"\r{len(r['words'])} words in {time.time() - t:.0f} s -> {out}")


if __name__ == "__main__":
    main()
