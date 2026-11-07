#!/usr/bin/env python3
"""Local review: play a draft in the browser and leave frame-accurate notes, no upload.

    python3 server.py --video DRAFT.mp4 --notes NOTES.json [--markers MARKERS.json]
                      [--fps 25] [--start-tc 00:00:00:00] [--title "Draft 4"] [--port 8765] [--open]

Serves review.html, the video (with Range requests, so a 7 GB file seeks instantly),
Claude's markers (read only), the reviewer's notes (saved on every change), the export's transcript
(made in the background on first open) and its comparison with the last draft. Binds to
127.0.0.1 only: nothing leaves the Mac. Stop it with Ctrl+C.

Notes file (written by the page, read by Claude):
    {"video": ..., "fps": 25, "title": ..., "updated": ...,
     "notes": [{"id", "frame", "tc", "end_frame", "end_tc", "text", "created", "updated",
                "kind": "keep" or "rule" (absent means a change), "quote": the words highlighted,
                "marker_id": the marker it replies to, "image": path of a grabbed still}],
     "markers_checked": [marker id, ...],
     "markers_seen": [the list on the page], "video_stat": {"size", "mtime"}}
The last two make a notes file complete on its own, so the next draft can tell what was okayed.
Markers file (written by Claude before the review):
    {"markers": [{"id": "m1", "frame": 6291, "text": "Claude, check here: ..."}]}
"""
import argparse
import json
import mimetypes
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import drafts       # noqa: E402
import transcribe   # noqa: E402

CHUNK = 1 << 20
MAX_NOTES_BYTES = 5 << 20
LOCK = threading.Lock()
LAST = [0.0]   # time of the last request, for --idle-exit
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm"}


def tc_to_frames(tc, fps):
    h, m, s, f = (int(x) for x in re.split("[:;]", tc))
    return ((h * 60 + m) * 60 + s) * round(fps) + f   # non-drop: labels count at the nominal rate


def archive_stale_review(cfg):
    """A re-export under the same name: last draft's ticks would land on different markers, so
    its notes file becomes -review-draft-K.json, untouched, and this draft starts clean."""
    n, stat = cfg["notes"], transcribe.video_stat(cfg["video"])
    saved = transcribe.load(n)
    if not saved or not saved.get("video_stat") or saved["video_stat"] == stat or saved.get("video") != str(cfg["video"]):
        return
    base = n.name[:-len("-review.json")] if n.name.endswith("-review.json") else n.stem
    nums = [int(m.group(1)) for p in n.parent.glob(f"{glob_escape(base)}-review-draft-*.json")
            for m in [re.search(r"-review-draft-(\d+)\.json$", p.name)] if m]
    os.replace(n, n.with_name(f"{base}-review-draft-{max(nums, default=0) + 1}.json"))


def glob_escape(s):
    return re.sub(r"([*?\[])", r"[\1]", s)


def find_previous(cfg):
    """The last draft: an archived notes file for this name, or draft-(K-1) beside this file."""
    n, video = cfg["notes"], cfg["video"]
    base = n.name[:-len("-review.json")] if n.name.endswith("-review.json") else n.stem
    found = []
    for p in n.parent.glob(f"{glob_escape(base)}-review-draft-*.json"):
        m = re.search(r"-review-draft-(\d+)\.json$", p.name)
        if m:
            found.append((int(m.group(1)), p))
    if found:
        k, p = max(found)
        saved = transcribe.load(p) or {}
        stat = saved.get("video_stat")
        transcript = None
        if stat:
            for t in n.parent.glob(f"{glob_escape(video.stem)}-transcript*.json"):
                if transcribe.describes(transcribe.load(t), stat):
                    transcript = t
                    break
        return {"label": f"draft {k}", "markers": saved.get("markers_seen") or [], "checked": saved.get("markers_checked"),
                "notes": saved.get("notes"), "transcript": transcript, "video": None}
    m = re.search(r"draft-(\d+)", video.stem)
    if not m:
        return None
    from launch import places, transcript_path
    for k in range(int(m.group(1)) - 1, 0, -1):
        stem = re.sub(r"-premiere$", "", video.stem.replace(m.group(0), f"draft-{k}"))
        olds = sorted((p for p in video.parent.iterdir() if p.suffix.lower() in VIDEO_EXT and p.stem in (stem, stem + "-premiere")),
                      key=lambda p: p.stem)
        if not olds:
            continue
        old = olds[0]
        _, notes, markers = places(old)
        saved = transcribe.load(notes) or {}
        listed = saved.get("markers_seen") or (transcribe.load(markers) or {}).get("markers") or []
        return {"label": f"draft {k}", "markers": listed, "checked": saved.get("markers_checked"), "notes": saved.get("notes"),
                "transcript": transcript_path(old), "video": old}
    return None


def prepare(cfg):
    """Runs behind the page: the transcript first, then the comparison with the last draft."""
    st, out, video = cfg["status"], cfg["transcript"], cfg["video"]
    if not out:
        st["transcript"] = {"status": "off"}
        st["compare"] = {"status": "none"}
        return
    try:
        if not transcribe.is_fresh(out, video):
            st["transcript"] = {"status": "working", "pct": 0}
            transcribe.make(video, out, lambda pct: st["transcript"].update(pct=pct))
        st["transcript"] = {"status": "ready"}
    except Exception as e:
        print(f"Transcript failed: {e}", flush=True)
        st["transcript"] = {"status": "failed", "error": str(e)}
        st["compare"] = {"status": "none"}
        return
    try:
        prev = find_previous(cfg)
        if not prev:
            st["compare"] = {"status": "none"}
            return
        st["compare"] = {"status": "working", "label": prev["label"]}
        old_path = prev["transcript"]
        if prev["video"] and not transcribe.is_fresh(old_path, prev["video"]):
            transcribe.make(prev["video"], old_path)
        old = transcribe.load(old_path) if old_path else None
        if not old:
            st["compare"] = {"status": "none", "label": prev["label"], "why": "no transcript of the last draft to compare with"}
            return
        new = transcribe.load(out)
        cache = out.with_name(out.stem.replace("-transcript", "") + "-compare.json")
        key = {"old": [old["size"], old["mtime"]], "new": [new["size"], new["mtime"]]}
        hit = transcribe.load(cache)
        if hit and hit.get("key") == key:
            cmp = hit
        else:
            cmp = {"key": key, **drafts.compare(old["words"], new["words"])}
            cache.write_text(json.dumps(cmp, ensure_ascii=False))
        cfg["previous"], cfg["comparison"] = prev, cmp
        st["compare"] = {"status": "ready", "label": prev["label"], "changes": cmp["changes"]}
    except Exception as e:
        print(f"Comparison failed: {e}", flush=True)
        st["compare"] = {"status": "failed", "error": str(e)}


class Handler(BaseHTTPRequestHandler):
    server_version = "LocalReview/1"

    def log_message(self, fmt, *args):   # quiet; errors still print
        pass

    def send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def allowed(self):
        """Only this page may use this server, not some website the browser also has open."""
        host = self.headers.get("Host", "")
        origin = self.headers.get("Origin")
        if host.split(":")[0] not in ("127.0.0.1", "localhost") or (origin and origin != f"http://{host}"):
            self.send_error(403)
            return False
        return True

    def do_GET(self):
        LAST[0] = time.time()
        if not self.allowed():
            return
        cfg = self.server.cfg
        path = self.path.split("?", 1)[0]
        if path == "/api/ping":
            return self.send_json({"ok": True})
        if path in ("/", "/index.html"):
            return self.send_file(HERE / "review.html", "text/html; charset=utf-8")
        if path == "/video":
            return self.send_file(cfg["video"], mimetypes.guess_type(str(cfg["video"]))[0] or "video/mp4", ranged=True)
        if path == "/api/config":
            return self.send_json({"title": cfg["title"], "fps": cfg["fps"], "start_frame": cfg["start_frame"],
                                   "video": str(cfg["video"]), "notes_path": str(cfg["notes"])})
        if path == "/api/markers":
            m = cfg["markers"]
            return self.send_json(json.loads(m.read_text()) if m and m.exists() else {"markers": []})
        if path == "/api/notes":
            n = cfg["notes"]
            return self.send_json(json.loads(n.read_text()) if n.exists() else {"notes": [], "markers_checked": []})
        if path == "/api/status":
            st = dict(cfg["status"])
            if st["compare"].get("status") == "ready":
                m = cfg["markers"]
                listed = (json.loads(m.read_text()).get("markers") or []) if m and m.exists() else []
                listed = [{**x, "id": x.get("id") or f"m{i + 1}"} for i, x in enumerate(listed)]
                st["compare"] = {**st["compare"], "okayed": drafts.carried(cfg["previous"], listed, cfg["comparison"], cfg["fps"])}
            return self.send_json(st)
        if path == "/api/transcript":
            t = transcribe.load(cfg["transcript"]) if cfg["transcript"] else None
            return self.send_json({"words": t["words"]} if t else {"words": []})
        if path == "/api/siblings":
            here = cfg["video"]
            return self.send_json({"videos": [{"name": p.name, "current": p == here} for p in sorted(here.parent.iterdir())
                                              if p.suffix.lower() in VIDEO_EXT and not p.name.startswith(".")]})
        if path.startswith("/frames/"):
            name = path[len("/frames/"):]
            if not re.fullmatch(r"[0-9-]+\.png", name):
                return self.send_error(404)
            return self.send_file(frames_dir(cfg) / name, "image/png")
        self.send_error(404)

    def do_POST(self):
        LAST[0] = time.time()
        if not self.allowed():
            return
        cfg = self.server.cfg
        path = self.path.split("?", 1)[0]
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n)) if 0 < n < 10000 else {}
        except ValueError:
            return self.send_error(400)
        if path == "/api/grab":
            return self.grab(cfg, body)
        if path == "/api/open":
            return self.open_another(cfg, body)
        self.send_error(404)

    def grab(self, cfg, body):
        """Save the exact frame on screen as a full-size still beside the notes."""
        try:
            frame = max(0, int(body["frame"]))
        except (KeyError, TypeError, ValueError):
            return self.send_error(400)
        ffmpeg = transcribe.tool("ffmpeg")
        if not ffmpeg:
            return self.send_json({"error": "ffmpeg is missing"}, 500)
        f = frame + cfg["start_frame"]
        base = round(cfg["fps"])
        s = f // base
        name = f"{s // 3600:02}-{s // 60 % 60:02}-{s % 60:02}-{f % base:02}.png"
        out = frames_dir(cfg) / name
        out.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run([ffmpeg, "-nostdin", "-v", "error", "-y", "-ss", f"{max(0, frame - 0.25) / cfg['fps']:.4f}", "-i", str(cfg["video"]),
                            "-frames:v", "1", str(out)], capture_output=True, text=True)
        if r.returncode or not out.exists():
            return self.send_json({"error": "couldn't save that frame"}, 500)
        self.send_json({"url": f"/frames/{name}", "path": str(out)})

    def open_another(self, cfg, body):
        """Another video in its own tab: one from this folder, or one chosen in a Mac dialog."""
        launcher = [sys.executable, str(HERE / "launch.py")]
        if body.get("choose"):
            r = subprocess.run(["osascript", "-e", "activate", "-e",
                                'POSIX path of (choose file with prompt "Choose a video to review" of type {"public.movie"})'],
                               capture_output=True, text=True)
            if r.returncode:
                return self.send_json({"cancelled": True})
            r = subprocess.run(launcher + [r.stdout.strip()], capture_output=True, text=True)
        else:
            target = cfg["video"].parent / Path(str(body.get("name", ""))).name
            if target.suffix.lower() not in VIDEO_EXT or not target.is_file():
                return self.send_error(404)
            extra = [] if body.get("open") else ["--no-open"]
            r = subprocess.run(launcher + [str(target)] + extra, capture_output=True, text=True)
        if r.returncode or not r.stdout.strip():
            return self.send_json({"error": (r.stderr or r.stdout).strip()[:300] or "couldn't open it"}, 500)
        self.send_json({"url": r.stdout.strip().splitlines()[0]})

    def do_PUT(self):
        LAST[0] = time.time()
        if not self.allowed():
            return
        cfg = self.server.cfg
        if self.path.split("?", 1)[0] != "/api/notes":
            return self.send_error(404)
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > MAX_NOTES_BYTES:
            return self.send_error(413)
        try:
            data = json.loads(self.rfile.read(n))
            assert isinstance(data.get("notes"), list)
        except Exception:
            return self.send_error(400, "notes must be JSON with a notes list")
        data.update({"video": str(cfg["video"]), "fps": cfg["fps"], "title": cfg["title"],
                     "video_stat": transcribe.video_stat(cfg["video"]),
                     "updated": datetime.now().isoformat(timespec="seconds")})
        out = cfg["notes"]
        with LOCK:   # write to a temp file, then rename, so a crash never leaves half a file
            out.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=out.parent, prefix=".notes-", suffix=".json")
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            os.replace(tmp, out)
        self.send_json({"ok": True, "saved": data["updated"], "count": len(data["notes"])})

    def send_file(self, p, ctype, ranged=False):
        p = Path(p)
        if not p.exists():
            return self.send_error(404)
        size = p.stat().st_size
        start, end = 0, size - 1
        rng = self.headers.get("Range") if ranged else None
        m = re.match(r"bytes=(\d*)-(\d*)$", rng or "")
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else size - 1
            else:
                start = max(0, size - int(m.group(2)))
            end = min(end, size - 1)
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(end - start + 1))
        if ranged:
            self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store" if not ranged else "private, max-age=0")
        self.end_headers()
        try:
            with open(p, "rb") as f:
                f.seek(start)
                left = end - start + 1
                while left > 0:
                    buf = f.read(min(CHUNK, left))
                    if not buf:
                        break
                    self.wfile.write(buf)
                    left -= len(buf)
        except (BrokenPipeError, ConnectionResetError):
            pass   # the browser cancels requests whenever it seeks


def frames_dir(cfg):
    return cfg["notes"].parent / f"{cfg['video'].stem}-frames"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--notes", required=True)
    ap.add_argument("--markers")
    ap.add_argument("--transcript", help="where this export's transcript lives; made in the background if missing")
    ap.add_argument("--fps", type=float, default=25, help="the export's frame rate, e.g. 25 or 29.97")
    ap.add_argument("--start-tc", default="00:00:00:00", help="the file's source start timecode")
    ap.add_argument("--title")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--open", action="store_true", help="open the page in the default browser")
    ap.add_argument("--idle-exit", type=int, default=0,
                    help="stop after this many seconds with no page open (the page pings every 30 s); 0 = never")
    a = ap.parse_args()
    video = Path(a.video).expanduser().resolve()
    if not video.exists():
        sys.exit(f"No such video: {video}")
    cfg = {"video": video, "notes": Path(a.notes).expanduser().resolve(),
           "markers": Path(a.markers).expanduser().resolve() if a.markers else None,
           "transcript": Path(a.transcript).expanduser().resolve() if a.transcript else None,
           "status": {"transcript": {"status": "working", "pct": 0}, "compare": {"status": "waiting"}},
           "fps": a.fps, "start_frame": tc_to_frames(a.start_tc, a.fps), "title": a.title or video.stem}
    archive_stale_review(cfg)
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    srv.cfg = cfg
    url = f"http://127.0.0.1:{a.port}/"
    print(f"Local review of {video.name} at {url}  (notes: {cfg['notes']})", flush=True)
    threading.Thread(target=prepare, args=(cfg,), daemon=True).start()
    if a.open:
        webbrowser.open(url)
    if a.idle_exit:
        LAST[0] = time.time() + 120   # time to open the page

        def watch():
            while time.time() - LAST[0] < a.idle_exit:
                time.sleep(10)
            print(f"No page open for {a.idle_exit} s; stopping.", flush=True)
            srv.shutdown()
        threading.Thread(target=watch, daemon=True).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    srv.server_close()


if __name__ == "__main__":
    main()
