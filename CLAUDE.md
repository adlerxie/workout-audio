# workout-audio

## Claude instructions

Before every `git commit`, update this CLAUDE.md with any new learnings from the conversation — plan changes, exercise swaps, schedule decisions, user preferences. Then include CLAUDE.md in the commit.

Personal workout audio coaching system. Generates TTS-guided MP3 workout sessions and hosts an interactive weekly schedule website.

## Goal

Reduce diastolic blood pressure through consistent strength training + cardio. All session design reflects this (APT correction, isometric exercises for BP, glute/core focus).

## How to run

```bash
pip install -r requirements.txt
python generate_sessions.py
```

Outputs 3 MP3 files in the project root:
- `session1_lower_hip.mp3` — Lower body / hip dominant (Tuesday, ~40 min)
- `session2_upper_push.mp3` — Upper body push (Thursday, ~35 min)
- `session3_total_body.mp3` — Total body / core (Sunday optional, ~40 min)

## Key files

| File | Purpose |
|------|---------|
| `generate_sessions.py` | Main script — defines all sessions and generates MP3s via gTTS + pydub |
| `docs/schedule.html` | Interactive weekly schedule — open in browser, 4 tabs: Schedule / Week / Workouts / Walking |
| `docs/routine.md` | Full daily schedule, BP tracking guidance |
| `requirements.txt` | Python deps: gtts, pydub, audioop-lts, moviepy, requests, Pillow, numpy |
| `background music/` | 18 royalty-free tracks available for future music-mixed versions |
| `archive/` | Previous workout_a / workout_b audio versions |

## Session structure (generate_sessions.py)

Sessions are defined as Python dicts in `SESSIONS` (lines ~27–320). Each exercise has:
- `name`, `reps`/`duration`, `sets`
- `setup_cue` — form instruction before starting
- `go_cue` — initiation prompt
- `mid_cue` — form check at halfway point
- Timing for audio generation

`build(session)` assembles warm-up → main workout with rest → cooldown. `tts(text)` converts strings to AudioSegment via gTTS.

## Weekly schedule

- Mon / Tue / Thu / Fri — strength (4 sessions)
- Wed / Sat / Sun — rest
- Daily brisk walking in parallel (not scheduled, just a daily habit)

## Exercise tags in schedule.html

- `APT` — Anterior Pelvic Tilt correction exercises
- `BP` — Blood Pressure focused (isometric)
- `Core` — core stability
- `Iso` — isometric holds
- `light` — keep weight light (back sensitivity or BP caution)

## Notes

- MP3 and video files are gitignored (size). Regenerate from `generate_sessions.py`.
- `gif_cache/` holds downloaded ExerciseDB GIFs — also gitignored.
- `moviepy` dep is present for potential future video generation (not currently used in main flow).
- Exercise selection comes from the "Weight Training for Women" book (`docs/workout planning book/`).
