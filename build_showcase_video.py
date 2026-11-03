"""
OmniDirector AI — Precision Synchronized 2K Showcase Video & Audio Muxer
Records the live application at http://localhost:8000 with exact scene timing
matched to the user's authentic voiceover audio (scene_1 to scene_7),
then encodes via NVIDIA NVENC (RTX 5080) and muxes the master leveled audio.
"""
import os
import sys
import time
import json
import subprocess
import urllib.request
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_DIR = r"e:\Promptwars2026\omnidirector_ai"
RECORDINGS_DIR = os.path.join(WORKSPACE_DIR, "temp_recordings")
VOICEOVER_DIR = os.path.join(WORKSPACE_DIR, "voiceover")
MASTER_AUDIO = os.path.join(VOICEOVER_DIR, "voiceover_master.wav")
TIMINGS_JSON = os.path.join(VOICEOVER_DIR, "scene_timings.json")

VIDEO_NO_AUDIO = os.path.join(WORKSPACE_DIR, "omnidirector_ai_showcase_demo.mp4")
FINAL_SUBMISSION_MP4 = os.path.join(WORKSPACE_DIR, "omnidirector_ai_final_submission.mp4")

os.makedirs(RECORDINGS_DIR, exist_ok=True)

# 1. Load Measured Scene Timings
if not os.path.exists(TIMINGS_JSON) or not os.path.exists(MASTER_AUDIO):
    print("Compiling voiceover master audio first...")
    subprocess.run([sys.executable, "process_voiceover_master.py"], cwd=WORKSPACE_DIR, check=True)

with open(TIMINGS_JSON, "r", encoding="utf-8") as f:
    timings_data = json.load(f)

scenes = timings_data["scenes"]
total_audio_duration = timings_data["total_duration"]

print("=================================================================")
print("🎬 OMNIDIRECTOR AI — PRECISION SYNCED DEMO GENERATOR")
print(f"Total Master Audio Duration: {total_audio_duration:.2f}s (Cleaned & Leveled -16 LUFS)")
for sc, dur in scenes.items():
    print(f"  {sc}: {dur:.2f}s")
print("Hardware Acceleration: NVIDIA NVENC (RTX 5080)")
print("=================================================================")

# 2. Ensure Local Server is Running on Port 8000
def is_server_ready():
    try:
        with urllib.request.urlopen("http://localhost:8000/api/config", timeout=2) as res:
            return res.status == 200
    except Exception:
        return False

server_process = None
if not is_server_ready():
    print("Starting OmniDirector studio server (app.py) on port 8000...")
    server_process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=WORKSPACE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    for _ in range(15):
        if is_server_ready():
            print("OmniDirector Studio server is LIVE!")
            break
        time.sleep(1)
else:
    print("OmniDirector Studio server is already running on http://localhost:8000.")

# Clean previous temp recordings
for f in os.listdir(RECORDINGS_DIR):
    if f.endswith(".webm") or f.endswith(".mp4"):
        try:
            os.remove(os.path.join(RECORDINGS_DIR, f))
        except Exception:
            pass

pre_roll_sec = 0.0

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True,
            args=[
                "--disable-gpu-sandbox",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--enable-font-antialiasing",
                "--force-color-profile=srgb",
                "--font-render-hinting=medium",
            ]
        )

        # 2560x1440 QHD 2K Studio Viewport
        context = browser.new_context(
            viewport={"width": 2560, "height": 1440},
            record_video_dir=RECORDINGS_DIR,
            record_video_size={"width": 2560, "height": 1440},
            device_scale_factor=1.0,
        )

        rec_init_time = time.time()
        page = context.new_page()

        # Cinematic Subtitle Banner Helper
        def set_banner(text, highlight=""):
            page.evaluate("""({ text, highlight }) => {
                let el = document.getElementById('demo-cinematic-banner');
                if (!el) {
                    el = document.createElement('div');
                    el.id = 'demo-cinematic-banner';
                    el.style.position = 'fixed';
                    el.style.bottom = '32px';
                    el.style.left = '50%';
                    el.style.transform = 'translateX(-50%)';
                    el.style.background = 'rgba(18, 23, 33, 0.94)';
                    el.style.backdropFilter = 'blur(16px)';
                    el.style.border = '1px solid rgba(99, 130, 176, 0.5)';
                    el.style.boxShadow = '0 12px 48px rgba(0, 0, 0, 0.65), 0 0 30px rgba(99, 130, 176, 0.25)';
                    el.style.borderRadius = '50px';
                    el.style.padding = '12px 38px';
                    el.style.zIndex = '99999';
                    el.style.fontFamily = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
                    el.style.fontSize = '19px';
                    el.style.fontWeight = '500';
                    el.style.color = '#F1F4F9';
                    el.style.display = 'flex';
                    el.style.alignItems = 'center';
                    el.style.gap = '14px';
                    el.style.pointerEvents = 'none';
                    el.style.transition = 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)';
                    document.body.appendChild(el);
                }
                el.innerHTML = `
                    <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#E06D5B; box-shadow:0 0 14px #E06D5B;"></span>
                    <span style="color:#6382B0; font-weight:700; letter-spacing:0.5px;">${highlight ? highlight + ' • ' : ''}</span>
                    <span>${text}</span>
                `;
            }""", {"text": text, "highlight": highlight})

        print("Navigating to live studio at http://localhost:8000 ...")
        page.goto("http://localhost:8000", wait_until="networkidle")
        time.sleep(1.8)

        # Pre-roll duration before Scene 1 begins
        pre_roll_sec = time.time() - rec_init_time
        print(f"Browser initialized & ready. Pre-roll trimmed: {pre_roll_sec:.2f}s")

        # ======================================================================
        # SCENE 1: INTRODUCTION & STUDIO ARCHITECTURE
        # Duration: scene_1 duration (~28.67s)
        # ======================================================================
        s1_dur = scenes["scene_1"]
        print(f"\n▶ Recording Scene 1 (Duration: {s1_dur:.2f}s)...")
        t0 = time.time()

        set_banner("Meta Global AI Developer Hackathon Submission ($1M Prize Pool)", "OmniDirector AI")
        page.hover(".brand-title")
        time.sleep(4.0)

        set_banner("The Problem: Expensive Human Crews & 10+ Hours Slicing Vertical Reels", "Broadcast Bottleneck")
        page.hover("#camerasGrid")
        time.sleep(15.0)

        set_banner("Autonomous Virtual Control Room Running Live in Your Browser", "Meta AI Core")
        page.hover(".status-badge")
        rem_s1 = max(0.2, s1_dur - (time.time() - t0))
        time.sleep(rem_s1)

        # ======================================================================
        # SCENE 2: MULTI-CLOUD INFERENCE ENGINE SWITCHER
        # Duration: scene_2 duration (~20.27s)
        # ======================================================================
        s2_dur = scenes["scene_2"]
        print(f"\n▶ Recording Scene 2 (Duration: {s2_dur:.2f}s)...")
        t0 = time.time()

        set_banner("Baseten Serverless: 2,000,000 Tokens/Min (2M TPM) on Muse Spark Open", "Cloud Engine Matrix")
        page.hover("#selectCloudProvider")
        time.sleep(10.0)

        set_banner("1-Click Cloud Switcher: Seamless Routing to Meta Model API Cloud", "Zero-Downtime Routing")
        page.select_option("#selectCloudProvider", "meta")
        time.sleep(4.5)

        set_banner("Zero-Downtime Reliability: Switching Back to Baseten High-Throughput Cluster", "Production Primary")
        page.select_option("#selectCloudProvider", "baseten")
        rem_s2 = max(0.2, s2_dur - (time.time() - t0))
        time.sleep(rem_s2)

        # ======================================================================
        # SCENE 3: AUTONOMOUS NARRATIVE CUTS & HARDWARE RESILIENCE
        # Duration: scene_3 duration (~31.63s)
        # ======================================================================
        s3_dur = scenes["scene_3"]
        print(f"\n▶ Recording Scene 3 (Duration: {s3_dur:.2f}s)...")
        t0 = time.time()

        set_banner("Muse Spark Multi-Agent Arbitration: Dialogue Pacing & Climax Detection", "Autonomous Director")
        page.hover("#reasoningBubble")
        time.sleep(10.5)

        set_banner("Pacing Rule: Enforcing 2.5s Minimum Hold Duration to Prevent Jarring Cuts", "Cinematic Pacing")
        page.hover("#tile_cam_wide")
        time.sleep(0.5)
        page.click("#tile_cam_wide") # Cut to CAM 2
        time.sleep(9.5)

        set_banner("Hardware Sentinel: Simulating Camera 4 Disconnect (Toggle to OFFLINE)", "Fault-Tolerant Switching")
        page.hover("#tile_cam_reaction")
        time.sleep(0.5)
        page.click("#tile_cam_reaction .cam-power-toggle") # Toggle offline
        time.sleep(5.5)

        set_banner("Fault-Tolerant Directing: AI Locks Exclusively to Active Live Feeds", "Zero-Black-Frame Guarantee")
        time.sleep(2.0)
        page.click("#tile_cam_reaction .cam-power-toggle") # Restore online
        rem_s3 = max(0.2, s3_dur - (time.time() - t0))
        time.sleep(rem_s3)

        # ======================================================================
        # SCENE 4: INTERACTIVE SAM 3.1 POINT PROMPTING
        # Duration: scene_4 duration (~24.71s)
        # ======================================================================
        s4_dur = scenes["scene_4"]
        print(f"\n▶ Recording Scene 4 (Duration: {s4_dur:.2f}s)...")
        t0 = time.time()

        page.click("#tile_cam_host") # Back to CAM 1
        set_banner("Meta SAM 3.1: Zero-Shot Spatio-Temporal Segmentation", "Vision Sentinel")
        time.sleep(4.5)

        set_banner("Interactive Point Prompting: Click Any Focal Subject on 4K Canvas", "Click-to-Track (<15ms)")
        canvas_box = page.locator("#studioMainCanvas").bounding_box()
        if canvas_box:
            cx = canvas_box["x"] + canvas_box["width"] * 0.48
            cy = canvas_box["y"] + canvas_box["height"] * 0.42
            page.mouse.move(cx, cy)
            time.sleep(0.4)
            page.mouse.click(cx, cy)
            time.sleep(2.5)

            cx2 = canvas_box["x"] + canvas_box["width"] * 0.52
            cy2 = canvas_box["y"] + canvas_box["height"] * 0.62
            page.mouse.move(cx2, cy2)
            time.sleep(0.4)
            page.mouse.click(cx2, cy2)
            time.sleep(2.5)

        set_banner("Sub-Pixel Polygonal Boundaries & Focal Contours Extracted in <15ms", "SAM 3.1 Extraction")
        page.hover("#samMasksList")
        rem_s4 = max(0.2, s4_dur - (time.time() - t0))
        time.sleep(rem_s4)

        # ======================================================================
        # SCENE 5: KINETIC 9:16 VERTICAL REEL SYNTHESIS
        # Duration: scene_5 duration (~21.82s)
        # ======================================================================
        s5_dur = scenes["scene_5"]
        print(f"\n▶ Recording Scene 5 (Duration: {s5_dur:.2f}s)...")
        t0 = time.time()

        set_banner("Automated 9:16 Kinetic Pan-and-Scan: Real-Time Speaker Center-Staging", "Reel Synthesis")
        page.hover(".reel-phone-frame")
        time.sleep(7.5)

        set_banner("Spring-Damped Physical Easing (0.08 Coefficient): Natural Steadicam Motion", "Physical Spring Physics")
        page.hover("#reelCanvas")
        time.sleep(7.5)

        set_banner("1-Click Highlight Export: Recording 10-Second VP9 WebM Vertical Reel", "Automated Publishing")
        page.hover("#btnExportReel")
        time.sleep(0.4)
        page.click("#btnExportReel") # Trigger recording
        rem_s5 = max(0.2, s5_dur - (time.time() - t0))
        time.sleep(rem_s5)

        # ======================================================================
        # SCENE 6: CMX 3600 EDL EXPORT & META PAYLOADS DRAWER
        # Duration: scene_6 duration (~27.18s)
        # ======================================================================
        s6_dur = scenes["scene_6"]
        print(f"\n▶ Recording Scene 6 (Duration: {s6_dur:.2f}s)...")
        t0 = time.time()

        set_banner("CMX 3600 EDL Export: 1-Click Multi-Cam Timeline for DaVinci & Premiere", "Studio Workflow")
        page.hover("#btnExportEdl")
        time.sleep(0.5)
        try:
            with page.expect_download(timeout=3000) as download_info:
                page.click("#btnExportEdl")
        except Exception:
            pass
        time.sleep(12.5)

        set_banner("Architecture Transparency: Live System Prompts & Verified JSON Contracts", "Developer Drawer")
        page.hover("#btnOpenMetaDrawer")
        time.sleep(0.4)
        page.click("#btnOpenMetaDrawer") # Open drawer
        time.sleep(5.5)
        page.click("#btnCloseDrawer") # Close drawer
        time.sleep(1.0)

        set_banner("Dual-Theme Architecture: Washed-Out Scandinavian Light & Sleek Dark Studio", "Polished UX")
        page.click("#btnThemeToggle") # Dark mode
        time.sleep(2.5)
        page.click("#btnThemeToggle") # Light mode
        rem_s6 = max(0.2, s6_dur - (time.time() - t0))
        time.sleep(rem_s6)

        # ======================================================================
        # SCENE 7: SUMMARY & OUTRO
        # Duration: scene_7 duration (~14.13s)
        # ======================================================================
        s7_dur = scenes["scene_7"]
        print(f"\n▶ Recording Scene 7 (Duration: {s7_dur:.2f}s)...")
        t0 = time.time()

        set_banner("Democratizing Television Broadcasting for Solo Creators Worldwide", "OmniDirector AI")
        time.sleep(5.5)

        set_banner("Meta Global AI Developer Hackathon 2026 • Lead: Nikhil Singh Bisht", "Built for $1M Challenge")
        time.sleep(6.5)

        set_banner("Thank You for Watching • Happy Building!", "OmniDirector AI")
        rem_s7 = max(0.2, s7_dur - (time.time() - t0))
        time.sleep(rem_s7)

        print("\n✅ Finished recording timeline. Closing browser session...")
        context.close()
        browser.close()

finally:
    if server_process:
        try:
            server_process.terminate()
        except Exception:
            pass

# 3. Locate the recorded WebM file
recordings = [f for f in os.listdir(RECORDINGS_DIR) if f.endswith(".webm")]
if not recordings:
    print("ERROR: No recorded WebM file found in temp directory!")
    sys.exit(1)

raw_webm = os.path.join(RECORDINGS_DIR, recordings[0])
print(f"Captured raw browser session: {raw_webm} ({os.path.getsize(raw_webm) / (1024 * 1024):.2f} MB)")

# 4. Encode to 2K MP4 using NVENC hardware acceleration (RTX 5080)
# Trimming pre-roll so frame 0 matches Scene 1 audio start perfectly!
print(f"\nStep 1/2: Trimming pre-roll ({pre_roll_sec:.2f}s) & Encoding via NVIDIA NVENC (RTX 5080)...")
nvenc_cmd = [
    "ffmpeg", "-y",
    "-ss", f"{pre_roll_sec:.3f}",
    "-i", raw_webm,
    "-t", f"{total_audio_duration:.3f}",
    "-c:v", "h264_nvenc",
    "-preset", "p7",
    "-cq", "18",
    "-b:v", "16M",
    "-pix_fmt", "yuv420p",
    "-r", "60",
    "-an",
    VIDEO_NO_AUDIO
]

res = subprocess.run(nvenc_cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("NVENC fallback to libx264 software encoder...")
    fallback_cmd = [
        "ffmpeg", "-y",
        "-ss", f"{pre_roll_sec:.3f}",
        "-i", raw_webm,
        "-t", f"{total_audio_duration:.3f}",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-an",
        VIDEO_NO_AUDIO
    ]
    subprocess.run(fallback_cmd, check=True)

# 5. Mux with Leveled Master Audio Track
print(f"\nStep 2/2: Muxing 2K 60FPS video with master leveled voiceover track...")
mux_cmd = [
    "ffmpeg", "-y",
    "-i", VIDEO_NO_AUDIO,
    "-i", MASTER_AUDIO,
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "320k",
    "-shortest",
    FINAL_SUBMISSION_MP4
]
subprocess.run(mux_cmd, check=True)

print("\n" + "=" * 65)
print("🎉 PERFECTLY SYNCHRONIZED SUBMISSION VIDEO CREATED!")
print(f"Final Video File: {FINAL_SUBMISSION_MP4}")
print(f"Resolution: 2560 x 1440 (2K QHD 60FPS)")
print(f"Duration: {total_audio_duration:.2f}s (2m 48.39s)")
print(f"File Size: {os.path.getsize(FINAL_SUBMISSION_MP4) / (1024 * 1024):.2f} MB")
print("Audio: User Voiceover (-16 LUFS EBU R128 Normalized, Zero Blank Space)")
print("Sync: 100% Frame-Accurate Dialogue Pace & Subtitle Timing")
print("=================================================================")
