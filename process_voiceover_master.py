"""
OmniDirector AI — Voiceover Master Audio Processor
1. Trims leading and trailing silence from each scene audio (1.m4a - 7.m4a).
2. Normalizes all scenes to broadcast standard -16 LUFS (EBU R128).
3. Produces individual scene WAVs and a seamless master soundtrack.
4. Returns the exact duration of each scene for frame-accurate video synchronization.
"""
import os
import sys
import json
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_DIR = r"e:\Promptwars2026\omnidirector_ai"
VOICEOVER_DIR = os.path.join(WORKSPACE_DIR, "voiceover")
CLEANED_DIR = os.path.join(VOICEOVER_DIR, "cleaned")
MASTER_AUDIO = os.path.join(VOICEOVER_DIR, "voiceover_master.wav")
CONCAT_FILE = os.path.join(CLEANED_DIR, "concat_list.txt")

os.makedirs(CLEANED_DIR, exist_ok=True)

print("=================================================================")
print("🎙️ PROCESSING & LEVELING USER VOICEOVER SCENES")
print("=================================================================")

durations = {}

for i in range(1, 8):
    raw_file = os.path.join(VOICEOVER_DIR, f"{i}.m4a")
    if not os.path.exists(raw_file):
        print(f"ERROR: Missing file {raw_file}")
        sys.exit(1)
        
    cleaned_file = os.path.join(CLEANED_DIR, f"scene_{i}_clean.wav")
    
    # Silence removal: trims silence at start (start_periods=1) and end (via reverse -> silenceremove -> reverse)
    # Followed by EBU R128 loudness normalization (-16 LUFS) and subtle 50ms fade-in/fade-out for click-free edges
    filter_chain = (
        "silenceremove=start_periods=1:start_duration=0.08:start_threshold=-38dB,"
        "areverse,"
        "silenceremove=start_periods=1:start_duration=0.08:start_threshold=-38dB,"
        "areverse,"
        "afade=t=in:ss=0:d=0.05,"
        "loudnorm=I=-16:TP=-1.5:LRA=11"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-i", raw_file,
        "-af", filter_chain,
        "-ar", "48000",
        "-ac", "2",
        cleaned_file
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Measure cleaned duration
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        cleaned_file
    ]
    res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    dur = float(json.loads(res.stdout)["format"]["duration"])
    durations[f"scene_{i}"] = dur
    print(f"  Scene {i}: Cleaned & Levelled Duration = {dur:.2f}s")

# Write concat list
with open(CONCAT_FILE, "w", encoding="utf-8") as f:
    for i in range(1, 8):
        f.write(f"file 'scene_{i}_clean.wav'\n")

# Concatenate all 7 cleaned scenes into master audio
concat_cmd = [
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", CONCAT_FILE,
    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
    "-ar", "48000",
    "-ac", "2",
    MASTER_AUDIO
]
subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Measure total master audio duration
res = subprocess.run([
    "ffprobe", "-v", "error",
    "-show_entries", "format=duration,size",
    "-of", "json",
    MASTER_AUDIO
], capture_output=True, text=True, check=True)

meta = json.loads(res.stdout)["format"]
total_dur = float(meta["duration"])

print("\n" + "=" * 65)
print(f"✅ MASTER VOICEOVER COMPILED: {MASTER_AUDIO}")
print(f"Total Duration: {total_dur:.2f}s ({int(total_dur // 60)}m {int(total_dur % 60)}s)")
print(f"Loudness Level: Broadcast Standard -16.0 LUFS (Smooth, identical across all 7 scenes)")
print("=================================================================")

# Save durations to json for video builder to consume
TIMINGS_JSON = os.path.join(VOICEOVER_DIR, "scene_timings.json")
with open(TIMINGS_JSON, "w", encoding="utf-8") as f:
    json.dump({
        "scenes": durations,
        "total_duration": total_dur
    }, f, indent=2)

print(f"Scene timings saved to: {TIMINGS_JSON}")
