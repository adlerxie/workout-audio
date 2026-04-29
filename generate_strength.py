#!/usr/bin/env python3
"""
Strength Workout Audio Generator — Routine 2
Edit ROUTINE and ROUNDS at the top, then run: python generate_strength.py
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

MUSIC_FOLDER  = "background music"
OUTPUT_FILE   = "workout_strength.mp3"
MUSIC_VOLUME  = -18
ROUNDS        = 2
BETWEEN_ROUNDS_REST = 60

# ── Routine ───────────────────────────────────────────────────────────────────

ROUTINE = [
    {
        "name": "Chest press",
        "reps": "8 to 12 reps",
        "reps_time": 45,
        "setup":   "Lie on your back with dumbbells at chest height, elbows at 45 degrees. Or get into a push-up position if you prefer.",
        "go_cue":  "Press up and breathe out. Lower slowly on the way back down.",
        "mid_cue": "Good. Steady pace. Breathe out on every push.",
        "timed":   False,
    },
    {
        "name": "Tricep extension",
        "reps": "10 to 12 reps",
        "reps_time": 40,
        "setup":   "Hold one dumbbell with both hands above your head, arms fully extended. Use a light to moderate weight.",
        "go_cue":  "Lower the weight slowly behind your head. Keep your elbows pointing forward, close together.",
        "mid_cue": "Good. Light weight, full range. Elbows stay in.",
        "timed":   False,
    },
    {
        "name": "Dumbbell row",
        "reps": "10 reps each side",
        "reps_time": 55,
        "setup":   "Hinge forward at the hips, back flat, core braced. Dumbbell in one hand.",
        "go_cue":  "Pull toward your hip. Controlled movement — don't rush.",
        "mid_cue": "Switch sides. Same controlled pace. Back stays flat.",
        "timed":   False,
    },
    {
        "name": "Farmer carry",
        "reps": "30 to 45 seconds",
        "reps_time": 40,
        "setup":   "Pick up both dumbbells. Stand tall — shoulders back, core tight.",
        "go_cue":  "Walk slowly around your space. Breathe naturally. No slouching.",
        "mid_cue": "Keep walking. Tall posture. Shoulders down and back.",
        "timed":   True,
    },
    {
        "name": "Side plank",
        "reps": "15 to 25 seconds each side",
        "reps_time": 50,
        "setup":   "Lie on your side, prop up on your forearm. Stack your feet or stagger them for balance.",
        "go_cue":  "Lift your hips. Body in a straight line from head to feet. Breathe normally.",
        "mid_cue": "Switch to the other side. Same position. Hold steady.",
        "timed":   True,
    },
    {
        "name": "Glute bridge",
        "reps": "12 reps",
        "reps_time": 40,
        "setup":   "Lie on your back, knees bent, feet flat on the floor hip-width apart.",
        "go_cue":  "Press through your heels to lift your hips. Squeeze gently at the top.",
        "mid_cue": "Good. Full range each rep. Gentle squeeze at the top.",
        "timed":   False,
    },
    {
        "name": "Step-ups",
        "reps": "8 reps each leg",
        "reps_time": 55,
        "setup":   "Stand in front of a sturdy step or low box. Feet hip-width apart.",
        "go_cue":  "Step up with one foot, bring the other up to meet it. Slow and stable. Then step back down.",
        "mid_cue": "Switch to the other leg. Control every step. No rushing.",
        "timed":   False,
    },
    {
        "name": "Wall sit",
        "reps": "20 to 30 seconds",
        "reps_time": 30,
        "setup":   "Back flat against the wall. Slide down until your knees are at 90 degrees, feet shoulder-width apart.",
        "go_cue":  "Hold steady. Easy to moderate effort. Keep breathing.",
        "mid_cue": "Halfway. Breathe. Shoulders relaxed against the wall.",
        "timed":   True,
    },
]

ENCOURAGEMENT = [
    "Good work.",
    "Nice job.",
    "Well done.",
    "Great effort.",
    "Keep it up.",
    "Strong work.",
    "You've got this.",
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
    cursor = 0
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

    # Intro
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

            # Mid-exercise cue
            overlay_at(ex["mid_cue"], exercise_start + exercise_ms // 2)

            # Final countdown for timed exercises
            if ex.get("timed"):
                overlay_at("5, 4, 3, 2, 1.", exercise_start + exercise_ms - 5000)

            wait(exercise_ms)
            encourage()

            if not is_last:
                # 15-sec transition
                transition_start = cursor
                next_clip = tts(
                    f"Coming up: {next_ex['name']}. {next_ex['reps']}. "
                    f"{next_ex['setup']}"
                )
                m, s = divmod(cursor // 1000, 60)
                print(f"  [{m:02d}:{s:02d}]  [next-up] {next_ex['name']}")
                events.append((cursor, next_clip))
                cursor += len(next_clip) + 300

                elapsed = cursor - transition_start
                remaining = max(0, 15000 - elapsed)
                if remaining > 3500:
                    wait(remaining - 3200)
                    say("3, 2, 1.", gap_after=200)
                else:
                    wait(remaining)
            else:
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
    print(f"Building {ROUNDS}-round strength workout...\n")
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
