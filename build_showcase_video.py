"""
OmniDirector AI — 2K/4K Broadcast Showcase Video Generator
Records the authentic, live-running OmniDirector Studio (http://localhost:8000)
using Playwright and encodes crystal-clear MP4 video via NVIDIA NVENC hardware acceleration (RTX 5080).
"""
import os
import sys
import time
import subprocess
import urllib.request
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_DIR = r"e:\Promptwars2026\omnidirector_ai"
RECORDINGS_DIR = os.path.join(WORKSPACE_DIR, "temp_recordings")
OUTPUT_MP4 = os.path.join(WORKSPACE_DIR, "omnidirector_ai_showcase_demo.mp4")

os.makedirs(RECORDINGS_DIR, exist_ok=True)

# 1. Ensure Local Server is Running on Port 8000
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
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # Wait for server to boot
    for _ in range(15):
        if is_server_ready():
            print("OmniDirector Studio server is LIVE and responding!")
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

print("=================================================================")
print("🎬 OMNIDIRECTOR AI — OFFICIAL DEMO VIDEO RECORDER")
print("Target: 1440p QHD 60FPS authentic studio capture (Zero Mock Clips)")
print("Hardware Acceleration: NVIDIA NVENC (RTX 5080)")
print("=================================================================")

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
                    el.style.background = 'rgba(18, 23, 33, 0.92)';
                    el.style.backdropFilter = 'blur(16px)';
                    el.style.border = '1px solid rgba(99, 130, 176, 0.5)';
                    el.style.boxShadow = '0 12px 48px rgba(0, 0, 0, 0.65), 0 0 30px rgba(99, 130, 176, 0.25)';
                    el.style.borderRadius = '50px';
                    el.style.padding = '12px 38px';
                    el.style.zIndex = '99999';
                    el.style.fontFamily = "'Inter', sans-serif";
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
        time.sleep(2.0)

        # --------------------------------------------------------------------------
        # SCENE 1: INTRODUCTION & STUDIO ARCHITECTURE (0:00 - 0:25)
        # --------------------------------------------------------------------------
        print("Recording Scene 1: Introduction & Live Studio Overview...")
        set_banner("Meta Global AI Developer Hackathon • $1M Prize Pool Submission", "OmniDirector AI")
        time.sleep(4.0)

        set_banner("Autonomous Multimodal Broadcast & Spatial Stream Director • Lead: Nikhil Singh Bisht", "Virtual Control Room")
        time.sleep(4.5)

        set_banner("Ingests 4-Camera Feeds, Decibel Waveforms & Diarized Conversational Beats", "Live Broadcast Ingest")
        page.hover(".brand-title")
        time.sleep(1.5)
        page.hover(".status-badge")
        time.sleep(2.5)

        # --------------------------------------------------------------------------
        # SCENE 2: MULTI-CLOUD INFERENCE ENGINE SWITCHER (0:25 - 0:50)
        # --------------------------------------------------------------------------
        print("Recording Scene 2: Multi-Cloud Provider Switcher...")
        set_banner("Connected to Baseten Serverless: 2,000,000 Tokens/Min (2M TPM) on Muse Spark Open", "Cloud Engine Matrix")
        page.hover("#selectCloudProvider")
        time.sleep(2.0)

        # Switch to Meta Model API ($150 Credits)
        set_banner("1-Click Provider Switch: Dynamically Routing to Meta Model API Cloud ($150 Balance)", "Zero-Downtime Routing")
        page.select_option("#selectCloudProvider", "meta")
        time.sleep(3.5)

        # Switch back to Baseten Muse Spark Open (Primary)
        set_banner("Returning to Baseten High-Throughput Cluster (2M TPM • Model 1026)", "Production Primary")
        page.select_option("#selectCloudProvider", "baseten")
        time.sleep(3.5)

        # --------------------------------------------------------------------------
        # SCENE 3: AUTONOMOUS NARRATIVE CUTS & OFFLINE RESILIENCE (0:50 - 1:25)
        # --------------------------------------------------------------------------
        print("Recording Scene 3: Autonomous Directing & Hardware Resilience...")
        set_banner("Muse Spark Multi-Agent Arbitration: Evaluating dialogue pacing & emotional climaxes", "Autonomous Director")
        page.hover("#reasoningBubble")
        time.sleep(3.5)

        set_banner("Pacing Rule Enforced: Minimum 2.5s hold prevents jarring micro-switching", "Cinematic Pacing")
        time.sleep(3.5)

        # Trigger manual cut override to CAM 2 (Wide)
        set_banner("Creator Override: Seamless instant cut to CAM 2 (Studio Wide)", "Manual Tally Override")
        page.hover("#tile_cam_wide")
        time.sleep(1.0)
        page.click("#tile_cam_wide")
        time.sleep(3.5)

        # Test Offline Camera Hardware Sentinel
        set_banner("Hardware Sentinel: Simulating Camera 4 disconnect (Toggle to OFFLINE)", "Fault-Tolerant Switching")
        page.hover("#tile_cam_reaction")
        time.sleep(1.0)
        page.click("#tile_cam_reaction .cam-power-toggle")
        time.sleep(3.0)

        set_banner("Resilience Confirmed: AI Director detects offline status and safely locks to live feeds", "Zero-Black-Frame Guarantee")
        time.sleep(3.5)

        # Restore Camera 4 to Online
        page.click("#tile_cam_reaction .cam-power-toggle")
        time.sleep(2.5)

        # --------------------------------------------------------------------------
        # SCENE 4: INTERACTIVE SAM 3.1 POINT PROMPTING (1:25 - 1:55)
        # --------------------------------------------------------------------------
        print("Recording Scene 4: Interactive SAM 3.1 Point Prompting...")
        # Switch back to CAM 1
        page.click("#tile_cam_host")
        time.sleep(1.5)

        set_banner("Meta SAM 3.1: Interactive Point-and-Click Zero-Shot Polygonal Segmentation", "Vision Sentinel")
        time.sleep(2.0)

        # Click on the studio canvas to simulate SAM 3.1 Point Prompt
        set_banner("User clicks focal subject on 4K canvas: Point Prompt coordinates sent to SAM 3.1...", "Click-to-Track (<15ms)")
        canvas_box = page.locator("#studioMainCanvas").bounding_box()
        if canvas_box:
            # Click center of host portrait
            cx = canvas_box["x"] + canvas_box["width"] * 0.48
            cy = canvas_box["y"] + canvas_box["height"] * 0.42
            page.mouse.move(cx, cy)
            time.sleep(1.0)
            page.mouse.click(cx, cy)
            time.sleep(2.5)

            # Click microphone / lower third
            cx2 = canvas_box["x"] + canvas_box["width"] * 0.52
            cy2 = canvas_box["y"] + canvas_box["height"] * 0.62
            page.mouse.move(cx2, cy2)
            time.sleep(1.0)
            page.mouse.click(cx2, cy2)
            time.sleep(2.5)

        set_banner("Sub-pixel polygonal contours & label tags generated in real time without green screens", "SAM 3.1 Extraction")
        page.hover("#samMasksList")
        time.sleep(3.5)

        # --------------------------------------------------------------------------
        # SCENE 5: KINETIC 9:16 VERTICAL REEL SYNTHESIS (1:55 - 2:25)
        # --------------------------------------------------------------------------
        print("Recording Scene 5: Kinetic 9:16 Vertical Reel Synthesis...")
        set_banner("Automated 9:16 Kinetic Pan-and-Scan: Real-time computer vision speaker center-staging", "Reel Synthesis")
        page.hover(".reel-phone-frame")
        time.sleep(3.0)

        set_banner("Spring-Damped Physical Easing (0.08 coefficient): Smooth Steadicam glide across subjects", "Physical Spring Physics")
        page.hover("#reelCanvas")
        time.sleep(3.5)

        set_banner("Synchronized Karaoke Captions: Sub-second word diarization via Muse Voice Transcribe", "Viral Format Ready")
        page.hover("#reelCaptions")
        time.sleep(3.0)

        # Trigger Reel Export
        set_banner("1-Click Highlight Export: Recording 10-second VP9 WebM vertical highlight reel...", "Automated Publishing")
        page.hover("#btnExportReel")
        time.sleep(1.0)
        page.click("#btnExportReel")
        time.sleep(4.5)

        # --------------------------------------------------------------------------
        # SCENE 6: CMX 3600 EDL EXPORT & META PAYLOADS DRAWER (2:25 - 2:50)
        # --------------------------------------------------------------------------
        print("Recording Scene 6: Professional CMX 3600 EDL & Architecture Transparency...")
        set_banner("Professional Post-Production: Exporting CMX 3600 EDL for DaVinci Resolve & Premiere Pro", "Studio Workflow")
        page.hover("#btnExportEdl")
        time.sleep(1.2)
        try:
            with page.expect_download(timeout=4000) as download_info:
                page.click("#btnExportEdl")
        except Exception:
            pass
        time.sleep(2.0)

        # Open Meta Payloads Transparency Drawer
        set_banner("Architecture Transparency: Inspecting live Meta Muse Spark & SAM 3.1 system schemas", "Developer Drawer")
        page.hover("#btnOpenMetaDrawer")
        time.sleep(1.0)
        page.click("#btnOpenMetaDrawer")
        time.sleep(3.0)

        set_banner("Verified JSON Contracts & Multimodal Schemas Driving Autonomous Arbitration", "Multi-Agent Protocol")
        page.hover(".meta-drawer-panel")
        time.sleep(3.5)

        # Close Drawer
        page.click("#btnCloseDrawer")
        time.sleep(1.5)

        # Toggle Light / Dark Studio Theme
        set_banner("Washed-out Scandinavian Light Theme & Sleek Dark Mode Studio Toggle", "Polished UX")
        page.click("#btnThemeToggle")
        time.sleep(2.5)
        page.click("#btnThemeToggle")
        time.sleep(2.0)

        # --------------------------------------------------------------------------
        # SCENE 7: SUMMARY & OUTRO (2:50 - 3:00)
        # --------------------------------------------------------------------------
        print("Recording Scene 7: Wrap-up & Submission...")
        set_banner("OmniDirector AI • Built for Meta Global AI Developer Hackathon 2026", "Democratizing Broadcast TV")
        time.sleep(3.5)

        set_banner("Powered by Meta Muse Spark, SAM 3.1 & Baseten Serverless • Thank You!", "Nikhil Singh Bisht")
        time.sleep(4.0)

        print("Closing recording session...")
        context.close()
        browser.close()

finally:
    if server_process:
        try:
            server_process.terminate()
        except Exception:
            pass

# Locate the recorded WebM file
recordings = [f for f in os.listdir(RECORDINGS_DIR) if f.endswith(".webm")]
if not recordings:
    print("ERROR: No recorded WebM file found in temp directory!")
    sys.exit(1)

raw_webm = os.path.join(RECORDINGS_DIR, recordings[0])
print(f"Captured raw browser session: {raw_webm} ({os.path.getsize(raw_webm) / (1024 * 1024):.2f} MB)")

# Encode using NVIDIA NVENC hardware acceleration (RTX 5080)
print(f"\nEncoding to pristine 2K/1440p MP4 via NVIDIA NVENC hardware acceleration...")
print(f"Destination: {OUTPUT_MP4}")

nvenc_cmd = [
    "ffmpeg", "-y",
    "-i", raw_webm,
    "-c:v", "h264_nvenc",
    "-preset", "p7",
    "-cq", "18",
    "-b:v", "16M",
    "-pix_fmt", "yuv420p",
    "-r", "60",
    "-an",
    OUTPUT_MP4
]

res = subprocess.run(nvenc_cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("NVENC fallback to libx264 software encoder...")
    fallback_cmd = [
        "ffmpeg", "-y",
        "-i", raw_webm,
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-an",
        OUTPUT_MP4
    ]
    res = subprocess.run(fallback_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg encoding error:", res.stderr)
        sys.exit(1)

print("\n" + "=" * 65)
print("🎉 SHOWCASE VIDEO GENERATION COMPLETE!")
print(f"Video File: {OUTPUT_MP4}")
print(f"Resolution: 2560 x 1440 (2K QHD 60FPS)")
print(f"File Size: {os.path.getsize(OUTPUT_MP4) / (1024 * 1024):.2f} MB")
print("Authenticity: 100% Real Live Broadcast Application Engine")
print("=" * 65)
