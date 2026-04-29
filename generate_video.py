#!/usr/bin/env python3
"""
Workout Video Generator — Workout A
Generates an MP4 with animated exercise GIFs + voice cues.

Setup:
  1. pip install gtts pydub audioop-lts moviepy requests Pillow numpy
  2. ffmpeg installed (winget install ffmpeg)
  3. Free RapidAPI key → https://rapidapi.com
     Subscribe to ExerciseDB (free tier) → search "ExerciseDB" on RapidAPI
  4. Set RAPIDAPI_KEY below and run: python generate_video.py
"""

import io, os, re, requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from pydub import AudioSegment
from moviepy import VideoClip, AudioFileClip

# ── Config ────────────────────────────────────────────────────────────────────

RAPIDAPI_KEY        = "YOUR_RAPIDAPI_KEY_HERE"
OUTPUT_FILE         = "workout_a.mp4"
ROUNDS              = 2
BETWEEN_ROUNDS_REST = 60
GIF_CACHE_DIR       = "gif_cache"

W, H     = 1280, 720
FPS      = 12          # 12fps is fine for a workout video and renders faster
GIF_FPS  = 10          # playback speed for exercise GIFs
GIF_SIZE = (500, 500)

BG    = (18, 18, 28)
WHITE = (255, 255, 255)
GOLD  = (255, 200, 60)
GRAY  = (170, 170, 170)

# ── Routine ───────────────────────────────────────────────────────────────────
# "search" is the term sent to ExerciseDB — tune it if the wrong GIF comes back

ROUTINE = [
    {
        "name":      "Wall push-ups",
        "search":    "push up",
        "reps":      "10 reps",
        "reps_time": 45,
        "setup":     "Stand facing the wall, hands shoulder-width apart at chest height.",
        "go_cue":    "Breathe out as you push away from the wall.",
        "mid_cue":   "Good. Keep your core tight and breathe.",
        "timed":     False,
    },
    {
        "name":      "Dumbbell row",
        "search":    "dumbbell row",
        "reps":      "10 reps each side",
        "reps_time": 55,
        "setup":     "Hinge forward slightly, brace your core, keep your back flat.",
        "go_cue":    "Pull the weight up toward your hip. Keep your back steady.",
        "mid_cue":   "Switch sides. Same controlled movement.",
        "timed":     False,
    },
    {
        "name":      "Shoulder press",
        "search":    "dumbbell shoulder press",
        "reps":      "10 reps",
        "reps_time": 40,
        "setup":     "Hold dumbbells at shoulder height, palms facing forward.",
        "go_cue":    "Press straight up. Exhale on the way up, inhale on the way down.",
        "mid_cue":   "Great. Light weight, full range of motion.",
        "timed":     False,
    },
    {
        "name":      "Bicep curls",
        "search":    "dumbbell bicep curl",
        "reps":      "10 reps",
        "reps_time": 40,
        "setup":     "Stand tall, dumbbells at your sides, palms facing forward.",
        "go_cue":    "Curl up slowly. Keep your elbows tucked in at your sides.",
        "mid_cue":   "Keep breathing. No holding your breath.",
        "timed":     False,
    },
    {
        "name":      "Plank",
        "search":    "plank",
        "reps":      "30 seconds",
        "reps_time": 30,
        "setup":     "Get into a forearm plank or high plank on your hands.",
        "go_cue":    "Squeeze your core. Keep your hips level. Breathe normally.",
        "mid_cue":   "Halfway. Keep breathing. You're doing great.",
        "timed":     True,
    },
    {
        "name":      "Dead bug",
        "search":    "dead bug",
        "reps":      "10 reps each side",
        "reps_time": 60,
        "setup":     "Lie on your back. Arms pointing up, knees bent at 90 degrees.",
        "go_cue":    "Slowly lower opposite arm and leg. Press your lower back down.",
        "mid_cue":   "Slow and controlled. Lower back stays on the floor.",
        "timed":     False,
    },
    {
        "name":      "Wall sit",
        "search":    "wall sit",
        "reps":      "30 seconds",
        "reps_time": 30,
        "setup":     "Back flat against the wall. Slide down until knees are at 90 degrees.",
        "go_cue":    "Hold steady. Easy to moderate effort. Keep breathing.",
        "mid_cue":   "Halfway. Breathe. Shoulders relaxed.",
        "timed":     True,
    },
    {
        "name":      "Calf raises",
        "search":    "calf raise",
        "reps":      "15 reps",
        "reps_time": 60,
        "setup":     "Stand tall near a wall for balance. Feet hip-width apart.",
        "go_cue":    "Rise up slowly... and lower slowly. Control both directions.",
        "mid_cue":   "Nice and slow. Feel the squeeze at the top.",
        "timed":     False,
    },
]

ENCOURAGEMENT = ["Good work.", "Nice job.", "Well done.", "Great effort.", "Keep it up."]

# ── Fonts ─────────────────────────────────────────────────────────────────────

def _font(size):
    for path in [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

F_TITLE  = _font(58)
F_REPS   = _font(38)
F_CUE    = _font(28)
F_TIMER  = _font(72)

# ── GIF fetching ──────────────────────────────────────────────────────────────

os.makedirs(GIF_CACHE_DIR, exist_ok=True)

def fetch_gif_frames(name, search):
    slug = re.sub(r"[^a-z0-9]+", "_", search.lower()).strip("_")
    cache = os.path.join(GIF_CACHE_DIR, f"{slug}.gif")

    if not os.path.exists(cache):
        print(f"  Downloading GIF: {name} ("{search}")...")
        url = "https://exercisedb.p.rapidapi.com/exercises/name/" + requests.utils.quote(search)
        resp = requests.get(url, headers={
            "X-RapidAPI-Key":  RAPIDAPI_KEY,
            "X-RapidAPI-Host": "exercisedb.p.rapidapi.com",
        }, params={"limit": 1}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            print(f"  No match — using placeholder.")
            return _placeholder(name)
        gif_bytes = requests.get(data[0]["gifUrl"], timeout=15).content
        with open(cache, "wb") as f:
            f.write(gif_bytes)

    return _load_frames(cache, name)

def _load_frames(path, name):
    try:
        img = Image.open(path)
        frames = []
        while True:
            frames.append(img.copy().convert("RGBA").resize(GIF_SIZE, Image.LANCZOS))
            try:
                img.seek(img.tell() + 1)
            except EOFError:
                break
        return frames or _placeholder(name)
    except Exception:
        return _placeholder(name)

def _placeholder(name):
    img = Image.new("RGBA", GIF_SIZE, (50, 50, 70, 255))
    ImageDraw.Draw(img).text(
        (GIF_SIZE[0] // 2, GIF_SIZE[1] // 2), name,
        fill=WHITE, font=F_CUE, anchor="mm"
    )
    return [img]

# ── Frame renderer ────────────────────────────────────────────────────────────

def _wrap(text, chars=30):
    words, lines, line = text.split(), [], []
    for w in words:
        line.append(w)
        if len(" ".join(line)) > chars:
            if len(line) > 1:
                lines.append(" ".join(line[:-1]))
                line = [w]
    lines.append(" ".join(line))
    return lines

def render_frame(gif_frames, t, title, reps, cue, countdown=None):
    canvas = Image.new("RGB", (W, H), BG)
    draw   = ImageDraw.Draw(canvas)

    # GIF — left side, vertically centered
    frame = gif_frames[int(t * GIF_FPS) % len(gif_frames)].convert("RGBA")
    gy    = (H - GIF_SIZE[1]) // 2
    canvas.paste(frame, (40, gy), frame)

    # Text panel — right side
    tx = 40 + GIF_SIZE[0] + 50
    tw = W - tx - 40

    # Accent line
    draw.rectangle([tx, 80, tx + 4, H - 80], fill=GOLD)
    tx += 20

    # Title
    draw.text((tx, 130), title, fill=GOLD, font=F_TITLE)
    draw.text((tx, 210), reps,  fill=WHITE, font=F_REPS)

    # Cue text
    for i, ln in enumerate(_wrap(cue, 28)[:4]):
        draw.text((tx, 310 + i * 42), ln, fill=GRAY, font=F_CUE)

    # Countdown circle (bottom-right)
    if countdown is not None and countdown >= 0:
        cx, cy, r = W - 100, H - 100, 75
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=5)
        draw.text((cx, cy), str(max(0, int(countdown) + 1)),
                  fill=GOLD, font=F_TIMER, anchor="mm")

    return np.array(canvas)

# ── Rest / transition frame ───────────────────────────────────────────────────

def render_rest_frame(message="Get ready..."):
    canvas = Image.new("RGB", (W, H), BG)
    ImageDraw.Draw(canvas).text((W // 2, H // 2), message,
                                fill=WHITE, font=F_TITLE, anchor="mm")
    return np.array(canvas)

# ── Audio builder ─────────────────────────────────────────────────────────────

def _tts(text):
    fp = io.BytesIO()
    gTTS(text=text, lang="en", slow=False).write_to_fp(fp)
    fp.seek(0)
    return AudioSegment.from_mp3(fp)

def build_audio(routine, rounds):
    """Returns (audio_events, total_ms, exercise_windows).
    exercise_windows: list of (start_ms, end_ms, ex_index)
    """
    events   = []
    windows  = []
    cursor   = 0
    enc_idx  = [0]

    def say(text, gap=500):
        nonlocal cursor
        clip = _tts(text)
        events.append((cursor, clip))
        cursor += len(clip) + gap

    def overlay(text, pos):
        events.append((pos, _tts(text)))

    def wait(ms):
        nonlocal cursor
        cursor += ms

    def encourage():
        phrase = ENCOURAGEMENT[enc_idx[0] % len(ENCOURAGEMENT)]
        enc_idx[0] += 1
        say(phrase, gap=400)

    say(f"Let's get started. {rounds} rounds today. You've got this.", gap=2000)

    for rnd in range(1, rounds + 1):
        say(f"Round {rnd}.", gap=1000)

        for i, ex in enumerate(routine):
            is_last = i == len(routine) - 1
            next_ex = routine[i + 1] if not is_last else None

            say(f"{ex['name']}. {ex['reps']}.")
            say(ex["setup"], gap=300)
            say("3, 2, 1.", gap=200)
            say("Go! " + ex["go_cue"], gap=600)

            ex_start = cursor
            ex_ms    = ex["reps_time"] * 1000
            windows.append((ex_start, ex_start + ex_ms, i))

            overlay(ex["mid_cue"], ex_start + ex_ms // 2)
            if ex.get("timed"):
                overlay("5, 4, 3, 2, 1.", ex_start + ex_ms - 5000)

            wait(ex_ms)
            encourage()

            if not is_last:
                tr_start   = cursor
                next_clip  = _tts(f"Coming up: {next_ex['name']}. {next_ex['reps']}. {next_ex['setup']}")
                events.append((cursor, next_clip))
                cursor    += len(next_clip) + 300
                elapsed    = cursor - tr_start
                remaining  = max(0, 15000 - elapsed)
                if remaining > 3500:
                    wait(remaining - 3200)
                    say("3, 2, 1.", gap=200)
                else:
                    wait(remaining)
            else:
                if rnd < rounds:
                    say(f"Round {rnd} complete! Rest for {BETWEEN_ROUNDS_REST} seconds. Shake it out.", gap=1000)
                    wait((BETWEEN_ROUNDS_REST - 5) * 1000)
                    say(f"Round {rnd + 1} coming up. 5, 4, 3, 2, 1.", gap=500)
                else:
                    say("Workout complete! Great job today. Take a few minutes to stretch and cool down.", gap=0)

    return events, cursor, windows

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if RAPIDAPI_KEY == "YOUR_RAPIDAPI_KEY_HERE":
        print("ERROR: Set RAPIDAPI_KEY at the top of the script.")
        print("  1. Sign up free at https://rapidapi.com")
        print("  2. Search 'ExerciseDB' and subscribe (free tier)")
        print("  3. Copy your key into RAPIDAPI_KEY")
        return

    print("Fetching exercise GIFs...\n")
    gif_cache = {}
    for ex in ROUTINE:
        gif_cache[ex["name"]] = fetch_gif_frames(ex["name"], ex.get("search", ex["name"]))

    print(f"\nBuilding {ROUNDS}-round audio timeline...")
    audio_events, total_ms, windows = build_audio(ROUTINE, ROUNDS)
    total_sec = total_ms / 1000
    m, s = divmod(int(total_sec), 60)
    print(f"Duration: {m}m {s}s")

    # Build window lookup
    def active_exercise(t_ms):
        for start, end, idx in windows:
            if start <= t_ms < end:
                return idx, (t_ms - start) / 1000, (end - start) / 1000
        return None, 0, 0

    print("\nRendering video (this takes a few minutes)...")

    def make_frame(t):
        t_ms = t * 1000
        ex_idx, ex_t, ex_dur = active_exercise(t_ms)
        if ex_idx is not None:
            ex       = ROUTINE[ex_idx]
            cue      = ex["go_cue"] if ex_t < ex_dur / 2 else ex["mid_cue"]
            countdown = (ex_dur - ex_t - 1) if ex.get("timed") and ex_t > ex_dur - 6 else None
            return render_frame(gif_cache[ex["name"]], t, ex["name"], ex["reps"], cue, countdown)
        return render_rest_frame()

    video = VideoClip(make_frame, duration=total_sec).with_fps(FPS)

    print("Mixing audio...")
    bed = AudioSegment.silent(duration=total_ms)
    for ts, clip in audio_events:
        bed = bed.overlay(clip, position=ts)
    tmp_audio = "_tmp_audio.mp3"
    bed.export(tmp_audio, format="mp3", bitrate="192k")

    final = video.with_audio(AudioFileClip(tmp_audio))

    print(f"\nExporting → {OUTPUT_FILE}")
    final.write_videofile(OUTPUT_FILE, fps=FPS, codec="libx264",
                          audio_codec="aac", threads=4, logger="bar")
    os.remove(tmp_audio)
    print(f"\nDone! → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
