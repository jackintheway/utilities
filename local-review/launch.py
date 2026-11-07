#!/usr/bin/env python3
"""Open a video in the local reviewer: what Local Reviewer.app runs when a video is dropped on it.

    python3 launch.py VIDEO [--no-open]
    python3 launch.py VIDEO --paths     (print where the markers and notes go; start nothing)

Works out where the notes go, reads the frame rate and start timecode from the file, starts
server.py in the background (it stops itself 15 minutes after the page is closed) and opens
the page. If that video is already open in a running reviewer, it just opens that page again.

Where notes go:
  - a video in an exports/ folder with a notes/ folder beside it -> that notes/
  - anything else -> a review-notes/ folder next to the video
Names: <video name>-review.json and <video name>-markers.json (the markers Claude writes
before a review), so each version of a draft keeps its own. A ...-premiere render shares its
draft's files, since it is the same cut. Older reviews named just draft-K-review.json and
draft-K-markers.json keep working: if one exists for this draft and the full name doesn't,
it is used. The transcript is <video name>-transcript.json in the same folder, always on the
file's full name, since a -premiere render can differ by a frame or two.
"""
import json
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORTS = range(8765, 8785)
IDLE = 900
LOG = Path.home() / "Library/Logs/local-review.log"


def tool(name):
    return shutil.which(name) or next((p for p in (f"/opt/homebrew/bin/{name}", f"/usr/local/bin/{name}") if Path(p).exists()), None)


def probe(video):
    """Frame rate and start timecode, from ffprobe when it's there."""
    ff = tool("ffprobe")
    if not ff:
        return 25.0, "00:00:00:00"
    out = subprocess.run([ff, "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=r_frame_rate:stream_tags=timecode:format_tags=timecode", "-of", "json", str(video)],
                         capture_output=True, text=True).stdout
    try:
        d = json.loads(out)
        num, den = (int(x) for x in d["streams"][0]["r_frame_rate"].split("/"))
        fps = round(num / den, 3)
        tc = (d["streams"][0].get("tags", {}).get("timecode") or d.get("format", {}).get("tags", {}).get("timecode")
              or "00:00:00:00")
        return fps, tc.replace(";", ":")
    except Exception:
        return 25.0, "00:00:00:00"


def places(video):
    if video.parent.name == "exports" and (video.parent.parent / "notes").is_dir():
        folder = video.parent.parent / "notes"
    else:
        folder = video.parent / "review-notes"
    base = re.sub(r"-premiere$", "", video.stem)
    m = re.search(r"draft-(\d+)", base)
    has = lambda b: (folder / f"{b}-review.json").exists() or (folder / f"{b}-markers.json").exists()
    if m and not has(base) and has(f"draft-{m.group(1)}"):   # a review from before the full names
        base = f"draft-{m.group(1)}"
    return folder, folder / f"{base}-review.json", folder / f"{base}-markers.json"


def transcript_path(video):
    return places(video)[0] / f"{video.stem}-transcript.json"


def running(port):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/config", timeout=0.5) as r:
            return json.loads(r.read())
    except Exception:
        return None


def current(port):
    """A reviewer started before an update can't serve the new page's features, so don't reuse it."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status", timeout=0.5):
            return True
    except Exception:
        return False


def free(port):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    video = Path(args[0]).expanduser().resolve()
    if not video.is_file():
        sys.exit(f"Not a file: {video}")
    show = "--no-open" not in sys.argv
    if "--paths" in sys.argv:
        _, notes, markers = places(video)
        print(f"markers: {markers}\nnotes: {notes}\ntranscript: {transcript_path(video)}")
        return

    for port in PORTS:   # already open somewhere? reuse it
        cfg = running(port)
        if cfg and cfg.get("video") == str(video) and current(port):
            url = f"http://127.0.0.1:{port}/"
            if show:
                subprocess.run(["open", url])
            print(url)
            return

    port = next((p for p in PORTS if free(p)), None)
    if port is None:
        sys.exit("No free port between 8765 and 8784.")
    folder, notes, markers = places(video)
    folder.mkdir(parents=True, exist_ok=True)
    fps, tc = probe(video)
    title = re.sub(r"[-_]+", " ", video.stem)
    cmd = [sys.executable, str(HERE / "server.py"), "--video", str(video), "--notes", str(notes),
           "--markers", str(markers), "--transcript", str(transcript_path(video)), "--fps", str(fps), "--start-tc", tc, "--title", title,
           "--port", str(port), "--idle-exit", str(IDLE)]
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as log:
        log.write(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} {' '.join(cmd)}\n")
        subprocess.Popen(cmd, stdout=log, stderr=log, stdin=subprocess.DEVNULL, start_new_session=True)
    for _ in range(50):
        if running(port):
            break
        time.sleep(0.1)
    else:
        sys.exit(f"The reviewer didn't start; see {LOG}")
    url = f"http://127.0.0.1:{port}/"
    if show:
        subprocess.run(["open", url])
    print(url)
    print(f"notes: {notes}")


if __name__ == "__main__":
    main()
