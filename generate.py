#!/usr/bin/env python3
"""
Workout Audio Generator
Edit ROUTINE and ROUNDS at the top, then run: python generate.py
AirDrop the output MP3 to your iPhone.

Requires: pip install gtts pydub
          ffmpeg installed (brew install ffmpeg / winget install ffmpeg)
"""

import io
import os
from gtts import gTTS
from pydub import AudioSegment

# ── Config ────────────────────────────────────────────────────────────────────

MUSIC_FILE    = "music.mp3"
OUTPUT_FILE   = "workout.mp3"
MUSIC_VOLUME  = -14   # dB — lower = quieter background music
ROUNDS        = 2     # set to 3 when ready
BETWEEN_ROUNDS_REST = 60  # seconds of rest between rounds

# ── Routine ───────────────────────────────────────────────────────────────────
# reps_time: estimated seconds to complete the reps (used for voice timing)

ROUTINE = [
    {
        "name": "Wall push-ups",
        "reps": "8 to 12 reps",
        "note": "Breathe out when pushing.",
        "reps_time": 45,
    },
    {
        "name": "Dumbbell row",
        "reps": "10 reps each side",
        "note": "Keep your back steady throughout.",
        "reps_time": 55,
    },
    {
        "name": "Shoulder press",
        "reps": "8 to 10 reps",
        "note": "Use light to moderate weight.",
        "reps_time": 40,
    },
    {
        "name": "Bicep curls",
        "reps": "10 to 12 reps",
        "note": "No breath holding — keep breathing.",
        "reps_time": 40,
    },
    {
        "name": "Plank",
        "reps": "20 to 30 seconds",
        "note": "Breathe normally. Hold steady.",
        "reps_time": 30,
    },
    {
        "name": "Dead bug",
        "reps": "10 reps each side",
        "note": "Move slow and controlled.",
        "reps_time": 60,
    },
    {
        "name": "Wall sit",
        "reps": "20 to 30 seconds",
        "note": "Easy to moderate effort. Keep breathing.",
        "reps_time": 30,
    },
    {
        "name": "Calf raises",
        "reps": "12 to 15 reps",
        "note": "Slow up, slow down.",
        "reps_time": 50,
    },
]

# ── TTS ───────────────────────────────────────────────────────────────────────

def tts(text: str) -> AudioSegment:
    fp = io.BytesIO()
    gTTS(text=text, lang="en", slow=False).write_to_fp(fp)
    fp.seek(0)
    return AudioSegment.from_mp3(fp)

def silence(ms: int) -> AudioSegment:
    return AudioSegment.silent(duration=ms)

# ── Timeline ──────────────────────────────────────────────────────────────────

def build_timeline(routine, rounds):
    events = []
    cursor = 0  # ms

    def say(text, gap_after=500):
        nonlocal cursor
        clip = tts(text)
        m, s = divmod(cursor // 1000, 60)
        print(f"  [{m:02d}:{s:02d}]  {text}")
        events.append((cursor, clip))
        cursor += len(clip) + gap_after

    def wait(ms):
        nonlocal cursor
        cursor += ms

    # ── Intro
    say(f"Let's get started. {rounds} rounds today. You've got this.", gap_after=1500)

    for round_num in range(1, rounds + 1):
        say(f"Round {round_num}.", gap_after=1000)

        for i, ex in enumerate(routine):
            is_last = (i == len(routine) - 1)
            next_ex = routine[i + 1] if not is_last else None

            # Announce exercise + note
            say(f"{ex['name']}. {ex['reps']}. {ex['note']}")
            say("Go!", gap_after=800)

            # Wait for reps
            wait(ex["reps_time"] * 1000)

            say("Good work.", gap_after=400)

            if not is_last:
                # 15-second transition: announce next exercise
                next_announce = tts(
                    f"Coming up next: {next_ex['name']}. "
                    f"{next_ex['reps']}. {next_ex['note']}"
                )
                announce_len = len(next_announce)
                events.append((cursor, next_announce))
                print(f"  [{cursor//60000:02d}:{(cursor%60000)//1000:02d}]  [next-up] {next_ex['name']}")
                cursor += announce_len + 400

                # Fill remaining time up to 15 seconds from start of transition
                transition_total = 15000  # 15 sec
                already_used = announce_len + 400
                remaining = max(0, transition_total - already_used)
                if remaining > 3000:
                    wait(remaining - 3000)
                    say("3, 2, 1.", gap_after=300)
                else:
                    wait(remaining)
            else:
                # End of round
                if round_num < rounds:
                    say(f"Round {round_num} done! Rest for {BETWEEN_ROUNDS_REST} seconds.", gap_after=1000)
                    rest_remaining = BETWEEN_ROUNDS_REST * 1000
                    if rest_remaining > 5000:
                        wait(rest_remaining - 5000)
                        say(f"Round {round_num + 1} starts in 5, 4, 3, 2, 1.", gap_after=500)
                    else:
                        wait(rest_remaining)
                else:
                    say("Workout complete! Great job. Take time to stretch and cool down.", gap_after=0)

    return events, cursor

# ── Mixer ─────────────────────────────────────────────────────────────────────

def mix(events, total_ms, music_file):
    if os.path.exists(music_file):
        music = AudioSegment.from_mp3(music_file) + MUSIC_VOLUME
        loops = (total_ms // len(music)) + 2
        bed = (music * loops)[:total_ms]
        print(f"\nMusic loaded: {music_file}")
    else:
        print(f"\nNo music file found at '{music_file}' — generating voice-only.")
        bed = silence(total_ms)

    for timestamp, clip in events:
        bed = bed.overlay(clip, position=timestamp)

    return bed

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Building {ROUNDS}-round workout timeline...\n")
    events, total_ms = build_timeline(ROUTINE, ROUNDS)

    m, s = divmod(total_ms // 1000, 60)
    print(f"\nTotal duration: {m}m {s}s  |  Voice cues: {len(events)}")

    print("\nMixing audio...")
    output = mix(events, total_ms, MUSIC_FILE)

    output.export(OUTPUT_FILE, format="mp3", bitrate="192k")
    print(f"\nSaved → {OUTPUT_FILE}")
    print("AirDrop to your iPhone and play in the Files or Music app.")

if __name__ == "__main__":
    main()
