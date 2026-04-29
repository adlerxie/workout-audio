#!/usr/bin/env python3
"""
Workout Audio Generator
Edit ROUTINE and ROUNDS at the top, then run: python generate.py
AirDrop the output MP3 to your iPhone.

Requires: pip install gtts pydub audioop-lts
          ffmpeg installed (brew install ffmpeg / winget install ffmpeg)
"""

import io
import os
import glob
import random
from gtts import gTTS
from pydub import AudioSegment

# ── Config ────────────────────────────────────────────────────────────────────

MUSIC_FOLDER  = "background music"   # folder with your MP3 tracks
OUTPUT_FILE   = "workout.mp3"
MUSIC_VOLUME  = -18   # dB — mild background (-14 louder, -22 very quiet)
ROUNDS        = 2     # change to 3 when ready
BETWEEN_ROUNDS_REST = 60  # seconds of rest between rounds

# ── Routine ───────────────────────────────────────────────────────────────────
# reps_time: estimated seconds to actually do the exercise
# setup:     said during the 15-sec transition (how to get into position)
# go_cue:    said right when exercise starts (form reminder)
# mid_cue:   said halfway through (encouragement / form check)
# timed:     True = countdown the last 5 seconds

ROUTINE = [
    {
        "name": "Wall push-ups",
        "reps": "8 to 12 reps",
        "reps_time": 45,
        "setup":   "Stand facing the wall, hands shoulder-width apart at chest height.",
        "go_cue":  "Breathe out as you push away from the wall.",
        "mid_cue": "Good. Keep your core tight and breathe.",
        "timed":   False,
    },
    {
        "name": "Dumbbell row",
        "reps": "10 reps each side",
        "reps_time": 55,
        "setup":   "Grab your dumbbell. Hinge forward slightly, brace your core, keep your back flat.",
        "go_cue":  "Pull the weight up toward your hip. Keep your back steady.",
        "mid_cue": "Switch sides. Same controlled movement.",
        "timed":   False,
    },
    {
        "name": "Shoulder press",
        "reps": "8 to 10 reps",
        "reps_time": 40,
        "setup":   "Hold dumbbells at shoulder height, palms facing forward.",
        "go_cue":  "Press straight up. Exhale on the way up, inhale on the way down.",
        "mid_cue": "Great. Light weight, full range of motion.",
        "timed":   False,
    },
    {
        "name": "Bicep curls",
        "reps": "10 to 12 reps",
        "reps_time": 40,
        "setup":   "Stand tall, dumbbells at your sides, palms facing forward.",
        "go_cue":  "Curl up slowly. Keep your elbows tucked in at your sides.",
        "mid_cue": "Keep breathing. No holding your breath.",
        "timed":   False,
    },
    {
        "name": "Plank",
        "reps": "20 to 30 seconds",
        "reps_time": 30,
        "setup":   "Get into a forearm plank or high plank on your hands.",
        "go_cue":  "Squeeze your core. Keep your hips level. Breathe normally.",
        "mid_cue": "Halfway. Keep breathing. You're doing great.",
        "timed":   True,
    },
    {
        "name": "Dead bug",
        "reps": "10 reps each side",
        "reps_time": 60,
        "setup":   "Lie on your back. Arms pointing up to the ceiling, knees bent at 90 degrees.",
        "go_cue":  "Slowly lower opposite arm and leg toward the floor. Press your lower back down.",
        "mid_cue": "Slow and controlled. Lower back stays on the floor the whole time.",
        "timed":   False,
    },
    {
        "name": "Wall sit",
        "reps": "20 to 30 seconds",
        "reps_time": 30,
        "setup":   "Back flat against the wall. Slide down until your knees are at 90 degrees.",
        "go_cue":  "Hold steady. Easy to moderate effort. Keep breathing.",
        "mid_cue": "Halfway. Breathe. Shoulders relaxed.",
        "timed":   True,
    },
    {
        "name": "Calf raises",
        "reps": "12 to 15 reps",
        "reps_time": 50,
        "setup":   "Stand tall near a wall for balance if needed. Feet hip-width apart.",
        "go_cue":  "Rise up slowly... and lower slowly. Control both directions.",
        "mid_cue": "Nice and slow. Feel the squeeze at the top.",
        "timed":   False,
    },
]

ENCOURAGEMENT = [
    "Good work.",
    "Nice job.",
    "Well done.",
    "Great effort.",
    "Keep it up.",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def tts(text: str) -> AudioSegment:
    fp = io.BytesIO()
    gTTS(text=text, lang="en", slow=False).write_to_fp(fp)
    fp.seek(0)
    return AudioSegment.from_mp3(fp)

def silence(ms: int) -> AudioSegment:
    return AudioSegment.silent(duration=ms)

def load_music(folder: str, total_ms: int) -> AudioSegment:
    files = glob.glob(os.path.join(folder, "*.mp3"))
    if not files:
        print(f"No MP3s found in '{folder}' — generating voice-only.")
        return silence(total_ms)

    random.shuffle(files)
    print(f"Music tracks ({len(files)}):")
    for f in files:
        print(f"  {os.path.basename(f)}")

    bed = AudioSegment.empty()
    while len(bed) < total_ms:
        for f in files:
            bed += AudioSegment.from_mp3(f)
            if len(bed) >= total_ms:
                break

    return (bed[:total_ms] + MUSIC_VOLUME)

# ── Timeline builder ──────────────────────────────────────────────────────────

def build_timeline(routine: list, rounds: int) -> tuple[list, int]:
    events = []
    cursor = 0  # ms
    encourage_idx = [0]

    def say(text, gap_after=500):
        nonlocal cursor
        clip = tts(text)
        m, s = divmod(cursor // 1000, 60)
        print(f"  [{m:02d}:{s:02d}]  {text}")
        events.append((cursor, clip))
        cursor += len(clip) + gap_after

    def overlay_at(text, position_ms):
        clip = tts(text)
        m, s = divmod(position_ms // 1000, 60)
        print(f"  [{m:02d}:{s:02d}]  {text}")
        events.append((position_ms, clip))

    def wait(ms):
        nonlocal cursor
        cursor += ms

    def encourage():
        phrase = ENCOURAGEMENT[encourage_idx[0] % len(ENCOURAGEMENT)]
        encourage_idx[0] += 1
        say(phrase, gap_after=400)

    # ── Intro
    say(f"Let's get started. {rounds} rounds today. You've got this.", gap_after=2000)

    for round_num in range(1, rounds + 1):
        say(f"Round {round_num}.", gap_after=1000)

        for i, ex in enumerate(routine):
            is_last = (i == len(routine) - 1)
            next_ex = routine[i + 1] if not is_last else None

            # Announce + setup
            say(f"{ex['name']}. {ex['reps']}.")
            say(ex["setup"], gap_after=300)
            say("3, 2, 1.", gap_after=200)
            say("Go! " + ex["go_cue"], gap_after=600)

            exercise_start = cursor
            exercise_ms = ex["reps_time"] * 1000

            # Mid-exercise cue at halfway point
            mid_point = exercise_start + exercise_ms // 2
            overlay_at(ex["mid_cue"], mid_point)

            # Countdown last 5 sec for timed holds
            if ex.get("timed"):
                countdown_at = exercise_start + exercise_ms - 5000
                overlay_at("5, 4, 3, 2, 1.", countdown_at)

            wait(exercise_ms)
            encourage()

            if not is_last:
                # 15-sec transition: announce next exercise + setup
                transition_start = cursor
                next_clip = tts(
                    f"Coming up: {next_ex['name']}. {next_ex['reps']}. "
                    f"{next_ex['setup']}"
                )
                m, s = divmod(cursor // 1000, 60)
                print(f"  [{m:02d}:{s:02d}]  [next-up] {next_ex['name']}")
                events.append((cursor, next_clip))
                cursor += len(next_clip) + 300

                # Fill to 15 seconds total transition, then countdown
                elapsed = cursor - transition_start
                remaining = max(0, 15000 - elapsed)
                if remaining > 3500:
                    wait(remaining - 3200)
                    say("3, 2, 1.", gap_after=200)
                else:
                    wait(remaining)
            else:
                # End of round
                if round_num < rounds:
                    say(f"Round {round_num} complete! Rest for {BETWEEN_ROUNDS_REST} seconds. Shake it out.", gap_after=1000)
                    wait((BETWEEN_ROUNDS_REST - 5) * 1000)
                    say(f"Round {round_num + 1} coming up. 5, 4, 3, 2, 1.", gap_after=500)
                else:
                    say("Workout complete! Great job today. Take a few minutes to stretch and cool down.", gap_after=0)

    return events, cursor

# ── Mixer ─────────────────────────────────────────────────────────────────────

def mix(events: list, total_ms: int) -> AudioSegment:
    print(f"\nLoading music...")
    bed = load_music(MUSIC_FOLDER, total_ms)

    for timestamp, clip in events:
        bed = bed.overlay(clip, position=timestamp)

    return bed

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Building {ROUNDS}-round workout...\n")
    events, total_ms = build_timeline(ROUTINE, ROUNDS)

    m, s = divmod(total_ms // 1000, 60)
    print(f"\nTotal: {m}m {s}s  |  Cues: {len(events)}")

    print("\nMixing...")
    output = mix(events, total_ms)

    output.export(OUTPUT_FILE, format="mp3", bitrate="192k")
    print(f"\nSaved → {OUTPUT_FILE}")
    print("AirDrop to iPhone and play in Files or Music app.")

if __name__ == "__main__":
    main()
