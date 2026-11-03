"""
OmniDirector AI — Voiceover Audio Merger
Merges user-recorded audio (voiceover.mp3, voiceover.wav, voiceover.m4a)
with the crystal-clear 2K/4K demo video using FFmpeg.
"""
import os
import sys
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_DIR = r"e:\Promptwars2026\omnidirector_ai"
VOICEOVER_DIR = os.path.join(WORKSPACE_DIR, "voiceover")
VIDEO_PATH = os.path.join(WORKSPACE_DIR, "omnidirector_ai_showcase_demo.mp4")
FINAL_OUTPUT = os.path.join(WORKSPACE_DIR, "omnidirector_ai_final_submission.mp4")

os.makedirs(VOICEOVER_DIR, exist_ok=True)

if not os.path.exists(VIDEO_PATH):
    print(f"ERROR: Video file not found: {VIDEO_PATH}")
    print("Please run `python build_showcase_video.py` first to generate the video.")
    sys.exit(1)

# Find audio file in voiceover directory
audio_files = [f for f in os.listdir(VOICEOVER_DIR) if f.lower().endswith(('.mp3', '.wav', '.m4a', '.aac', '.ogg'))]

if not audio_files:
    print("=================================================================")
    print("📢 NO VOICEOVER AUDIO FOUND YET!")
    print(f"Please drop your audio recording into: {VOICEOVER_DIR}")
    print("Acceptable formats: voiceover.mp3, voiceover.wav, voiceover.m4a")
    print("Once copied, run this script again: `python merge_voiceover.py`")
    print("=================================================================")
    sys.exit(0)

selected_audio = os.path.join(VOICEOVER_DIR, audio_files[0])
print(f"Found voiceover audio: {selected_audio}")
print(f"Merging with 2K showcase video: {VIDEO_PATH} ...")

ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-i", VIDEO_PATH,
    "-i", selected_audio,
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "320k",
    "-shortest",
    FINAL_OUTPUT
]

res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("FFmpeg error:", res.stderr)
    sys.exit(1)

print("\n" + "=" * 65)
print("🎉 FINAL SUBMISSION VIDEO READY!")
print(f"Output File: {FINAL_OUTPUT}")
print(f"File Size: {os.path.getsize(FINAL_OUTPUT) / (1024 * 1024):.2f} MB")
print("Ready to upload directly to YouTube for Cerebral Valley!")
print("=" * 65)
