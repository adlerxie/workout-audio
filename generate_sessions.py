#!/usr/bin/env python3
"""
Strength Session Audio Generator
Generates 3 voice-only MP3s: session1, session2, session3.
No music. Includes warm-up, main workout (sets + rest), and cooldown.

Run: python generate_sessions.py
"""

import io
from gtts import gTTS
from pydub import AudioSegment

# ── Helpers ───────────────────────────────────────────────────────────────────

def tts(text: str) -> AudioSegment:
    fp = io.BytesIO()
    gTTS(text=text, lang="en", slow=False).write_to_fp(fp)
    fp.seek(0)
    return AudioSegment.from_mp3(fp)

def silence(ms: int) -> AudioSegment:
    return AudioSegment.silent(duration=ms)

# ── Session definitions ────────────────────────────────────────────────────────

SESSIONS = [
    {
        "name":    "Session 1. Lower body. Hip dominant.",
        "output":  "session1_lower_hip.mp3",
        "warmup": [
            {
                "name": "Straight-leg kicks",
                "duration": 30,
                "cue": "Kick one leg straight forward, alternating sides. Keep your standing leg soft.",
            },
            {
                "name": "Butt kicks",
                "duration": 30,
                "cue": "Jog in place, heels kicking up toward your glutes. Light and easy.",
            },
            {
                "name": "World's greatest stretch",
                "duration": 50,
                "cue": "Step into a lunge, plant your hand beside your foot, and reach your other arm up to the sky. Alternate sides slowly.",
            },
            {
                "name": "Plank",
                "duration": 30,
                "cue": "Hold your plank. Core tight, hips level, breathe normally.",
            },
        ],
        "main": [
            {
                "name":     "Deadlift",
                "reps":     "8 reps",
                "reps_time": 45,
                "sets":     3,
                "setup":    "Stand with feet hip-width apart. Dumbbells in front of your thighs, soft bend in the knees, back flat.",
                "go_cue":   "Hinge at the hips, lower the weights along your legs, then drive through your heels to stand tall.",
                "mid_cue":  "Good. Keep the weights close to your body. Back stays flat.",
                "timed":    False,
            },
            {
                "name":     "Step-ups",
                "reps":     "8 reps each leg",
                "reps_time": 50,
                "sets":     3,
                "setup":    "Stand in front of a sturdy step or low box. Feet hip-width apart.",
                "go_cue":   "Step up with one foot, bring the other up to meet it. Slow and stable. Then step back down.",
                "mid_cue":  "Switch to the other leg. Control every step. No rushing.",
                "timed":    False,
            },
            {
                "name":     "Glute bridge",
                "reps":     "12 reps",
                "reps_time": 40,
                "sets":     3,
                "setup":    "Lie on your back, knees bent, feet flat on the floor hip-width apart.",
                "go_cue":   "Press through your heels to lift your hips. Squeeze gently at the top.",
                "mid_cue":  "Good. Full range each rep. Gentle squeeze at the top.",
                "timed":    False,
            },
            {
                "name":     "Good morning",
                "reps":     "10 reps",
                "reps_time": 40,
                "sets":     2,
                "setup":    "Stand tall, hands on hips or light dumbbells at your sides. Soft bend in the knees.",
                "go_cue":   "Hinge forward at the hips, keeping your back flat, until you feel a stretch in your hamstrings. Then stand back up.",
                "mid_cue":  "Slow and controlled. Feel the stretch in the back of your legs.",
                "timed":    False,
            },
            {
                "name":     "Wall sit",
                "reps":     "30 seconds",
                "reps_time": 30,
                "sets":     3,
                "setup":    "Back flat against the wall. Slide down until your knees are at 90 degrees.",
                "go_cue":   "Hold steady. Easy to moderate effort. Keep breathing.",
                "mid_cue":  "Halfway. Breathe. Shoulders relaxed.",
                "timed":    True,
            },
        ],
        "cooldown": [
            {
                "name": "Pretzel stretch",
                "duration": 60,
                "cue": "Lie on your back. Cross one ankle over the opposite knee and gently pull both legs toward your chest. Hold. Switch sides halfway.",
            },
            {
                "name": "Seated toe touch",
                "duration": 45,
                "cue": "Sit tall with legs straight out. Reach forward toward your toes. Hold the stretch. Breathe into it.",
            },
            {
                "name": "Standing calf stretch",
                "duration": 60,
                "cue": "Step one foot back, heel flat on the floor, front knee bent. Lean into the wall. Hold. Switch sides halfway.",
            },
            {
                "name": "Standing quad stretch",
                "duration": 60,
                "cue": "Stand on one leg, pull the other heel toward your glute. Hold onto a wall if needed. Switch sides halfway.",
            },
        ],
    },

    {
        "name":    "Session 2. Upper body. Chest, shoulders, and triceps.",
        "output":  "session2_upper_push.mp3",
        "warmup": [
            {
                "name": "Cross-body arm swing",
                "duration": 30,
                "cue": "Swing both arms across your chest and out wide. Keep it loose and rhythmic.",
            },
            {
                "name": "Shoulder rolls",
                "duration": 30,
                "cue": "Roll your shoulders forward 5 times, then backward 5 times. Nice and slow.",
            },
            {
                "name": "Up-down plank",
                "duration": 30,
                "cue": "Start in a forearm plank. Press up to a high plank one hand at a time, then lower back down. Alternate which hand leads.",
            },
            {
                "name": "T-spine rotation",
                "duration": 30,
                "cue": "Get into a half-kneeling position. Place one hand behind your head and rotate your upper back open toward the ceiling. Alternate sides.",
            },
        ],
        "main": [
            {
                "name":     "Push-ups",
                "reps":     "10 reps",
                "reps_time": 45,
                "sets":     3,
                "setup":    "Get into a high plank. Hands slightly wider than shoulder-width, core tight, body in a straight line.",
                "go_cue":   "Lower your chest to the floor slowly. Breathe in on the way down, breathe out as you push up.",
                "mid_cue":  "Good. Keep your hips level and core engaged. Slow and controlled.",
                "timed":    False,
            },
            {
                "name":     "Dumbbell shoulder press",
                "reps":     "10 reps",
                "reps_time": 40,
                "sets":     3,
                "setup":    "Hold dumbbells at shoulder height, palms facing forward. Stand tall or sit on a chair.",
                "go_cue":   "Press straight up. Exhale on the way up, inhale on the way down.",
                "mid_cue":  "Great. Light weight, full range of motion. Don't arch your back.",
                "timed":    False,
            },
            {
                "name":     "Standing tricep extension",
                "reps":     "10 reps",
                "reps_time": 40,
                "sets":     3,
                "setup":    "Hold one dumbbell with both hands above your head, arms fully extended.",
                "go_cue":   "Lower the weight slowly behind your head. Elbows pointing up, close to your ears. Don't let them flare out.",
                "mid_cue":  "Good. Light weight, full range. Elbows stay in.",
                "timed":    False,
            },
            {
                "name":     "Chest fly",
                "reps":     "10 reps",
                "reps_time": 40,
                "sets":     2,
                "setup":    "Lie on your back, dumbbells above your chest, slight bend in the elbows.",
                "go_cue":   "Open your arms wide and lower the weights out to the sides. Feel the stretch, then bring them back together.",
                "mid_cue":  "Good. Keep that soft bend in the elbows the whole time.",
                "timed":    False,
            },
            {
                "name":     "Plank",
                "reps":     "30 seconds",
                "reps_time": 30,
                "sets":     3,
                "setup":    "Get into a forearm plank or high plank on your hands.",
                "go_cue":   "Squeeze your core. Keep your hips level. Breathe normally.",
                "mid_cue":  "Halfway. Keep breathing. You're doing great.",
                "timed":    True,
            },
        ],
        "cooldown": [
            {
                "name": "Chest stretch",
                "duration": 45,
                "cue": "Clasp your hands behind your back, squeeze your shoulder blades together, and lift your arms slightly. Open your chest. Hold.",
            },
            {
                "name": "Standing biceps stretch",
                "duration": 40,
                "cue": "Extend one arm straight, palm facing up, and gently pull the fingers back with your other hand. Hold. Switch sides halfway.",
            },
            {
                "name": "Child's pose",
                "duration": 45,
                "cue": "Kneel and sit back toward your heels. Reach your arms forward on the floor. Let your back relax completely. Breathe slowly.",
            },
        ],
    },

    {
        "name":    "Session 3. Total body and core.",
        "output":  "session3_total_body.mp3",
        "warmup": [
            {
                "name": "Butt kicks",
                "duration": 30,
                "cue": "Jog in place, heels kicking up toward your glutes. Light and easy.",
            },
            {
                "name": "T-spine rotation",
                "duration": 30,
                "cue": "Half-kneeling. One hand behind your head. Rotate your upper back open toward the ceiling. Alternate sides.",
            },
            {
                "name": "Squat jack",
                "duration": 30,
                "cue": "Jump or step your feet wide and lower into a squat. Jump or step back together. Keep your chest up.",
            },
            {
                "name": "Knee hugs",
                "duration": 30,
                "cue": "Walk forward, pulling one knee up to your chest with each step. Tall posture. Alternate legs.",
            },
        ],
        "main": [
            {
                "name":     "Dead bug",
                "reps":     "10 reps each side",
                "reps_time": 60,
                "sets":     3,
                "setup":    "Lie on your back. Arms pointing up to the ceiling, knees bent at 90 degrees.",
                "go_cue":   "Slowly lower opposite arm and leg toward the floor. Press your lower back down the whole time.",
                "mid_cue":  "Slow and controlled. Lower back stays on the floor. That's the whole point.",
                "timed":    False,
            },
            {
                "name":     "Goblet squat",
                "reps":     "10 reps",
                "reps_time": 40,
                "sets":     3,
                "setup":    "Hold one dumbbell vertically at your chest with both hands. Feet shoulder-width apart, toes slightly out.",
                "go_cue":   "Sit down and back into the squat. Chest up, knees tracking over your toes. Drive through your heels to stand.",
                "mid_cue":  "Good. Full depth if comfortable. Chest stays up.",
                "timed":    False,
            },
            {
                "name":     "Glute bridge",
                "reps":     "12 reps",
                "reps_time": 40,
                "sets":     3,
                "setup":    "Lie on your back, knees bent, feet flat on the floor hip-width apart.",
                "go_cue":   "Press through your heels to lift your hips. Squeeze gently at the top.",
                "mid_cue":  "Good. Full range each rep. Gentle squeeze at the top.",
                "timed":    False,
            },
            {
                "name":     "Dumbbell row",
                "reps":     "10 reps each side",
                "reps_time": 55,
                "sets":     3,
                "setup":    "Hinge forward at the hips, back flat, core braced. Dumbbell in one hand.",
                "go_cue":   "Pull toward your hip. Controlled movement. Don't rush.",
                "mid_cue":  "Switch sides. Same controlled pace. Back stays flat.",
                "timed":    False,
            },
            {
                "name":     "Wall sit",
                "reps":     "30 seconds",
                "reps_time": 30,
                "sets":     3,
                "setup":    "Back flat against the wall. Slide down until your knees are at 90 degrees.",
                "go_cue":   "Hold steady. Easy to moderate effort. Keep breathing.",
                "mid_cue":  "Halfway. Breathe. Shoulders relaxed.",
                "timed":    True,
            },
        ],
        "cooldown": [
            {
                "name": "Cat-cow",
                "duration": 40,
                "cue": "On hands and knees. Arch your back up toward the ceiling, then let it sag toward the floor. Move slowly with your breath.",
            },
            {
                "name": "T-spine rotation",
                "duration": 40,
                "cue": "Half-kneeling. Hand behind your head. Rotate open slowly. Hold at the top. Alternate sides.",
            },
            {
                "name": "Child's pose",
                "duration": 45,
                "cue": "Sit back toward your heels, arms reaching forward on the floor. Let your back fully relax. Breathe slowly and deeply.",
            },
        ],
    },
]

REST_BETWEEN_SETS = 75   # seconds
WARMUP_GAP       = 500   # ms between warm-up moves (brief pause)
COOLDOWN_GAP     = 500

# ── Timeline builder ──────────────────────────────────────────────────────────

def build(session: dict) -> AudioSegment:
    print(f"\n{'─'*60}")
    print(f"Building: {session['output']}")
    print(f"{'─'*60}")

    track = AudioSegment.empty()

    def say(text, gap_after=500):
        nonlocal track
        clip = tts(text)
        ms = len(track)
        m, s = divmod(ms // 1000, 60)
        print(f"  [{m:02d}:{s:02d}]  {text[:80]}")
        track += clip + silence(gap_after)

    def hold(ms):
        nonlocal track
        track += silence(ms)

    def overlay(text, position_ms):
        clip = tts(text)
        m, s = divmod(position_ms // 1000, 60)
        print(f"  [{m:02d}:{s:02d}]  {text[:80]}")
        # Extend track if needed
        nonlocal track
        needed = position_ms + len(clip) - len(track)
        if needed > 0:
            track += silence(needed)
        track = track.overlay(clip, position=position_ms)

    # ── Intro
    say(session["name"], gap_after=1500)

    # ── Warm-up
    say("Warm-up. Follow along, no rest between movements.", gap_after=1000)

    for move in session["warmup"]:
        say(f"{move['name']}. {move['cue']}", gap_after=300)
        say("Go.", gap_after=400)
        hold(move["duration"] * 1000)

    say("Warm-up done. Take 20 seconds to shake it out.", gap_after=500)
    hold(20000)

    # ── Main workout
    say("Main workout. 3 sets per exercise. Rest between sets.", gap_after=1000)

    for ex in session["main"]:
        say(f"{ex['name']}. {ex['reps']}.", gap_after=300)
        say(ex["setup"], gap_after=500)

        for set_num in range(1, ex["sets"] + 1):
            say(f"Set {set_num}. 3, 2, 1.", gap_after=200)
            say("Go. " + ex["go_cue"], gap_after=500)

            ex_start = len(track)
            ex_ms    = ex["reps_time"] * 1000

            # Mid cue at halfway
            overlay(ex["mid_cue"], ex_start + ex_ms // 2)

            # Countdown last 5 sec for timed holds
            if ex.get("timed"):
                overlay("5, 4, 3, 2, 1.", ex_start + ex_ms - 5000)

            # Advance track to end of exercise
            needed = ex_start + ex_ms - len(track)
            if needed > 0:
                track += silence(needed)

            # Rest or finish
            if set_num < ex["sets"]:
                say(f"Rest. {REST_BETWEEN_SETS} seconds.", gap_after=500)
                # Count down last 5 sec of rest
                rest_start = len(track)
                hold((REST_BETWEEN_SETS - 5) * 1000)
                say("Coming up. 3, 2, 1.", gap_after=300)
            else:
                say("Good work.", gap_after=800)

    # ── Cooldown
    say("Main workout done. Time to cool down.", gap_after=1000)
    say("Hold each stretch. No rushing.", gap_after=800)

    for stretch in session["cooldown"]:
        say(f"{stretch['name']}.", gap_after=300)
        say(stretch["cue"], gap_after=400)
        hold(stretch["duration"] * 1000)
        say("Good.", gap_after=COOLDOWN_GAP)

    say("Session complete. Great work today.", gap_after=0)

    return track

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    for session in SESSIONS:
        audio = build(session)
        audio.export(session["output"], format="mp3", bitrate="192k")
        m, s = divmod(len(audio) // 1000, 60)
        print(f"\n  Saved → {session['output']}  ({m}m {s}s)")

    print("\nAll sessions done.")

if __name__ == "__main__":
    main()
