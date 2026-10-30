# 🎬 Meta Global AI Developer Hackathon — Official Submission Copy

**Submission Portal:** [Cerebral Valley / Devpost Event Portal](https://cerebralvalley.ai/e/meta-ai-developer-hackathon)  
**Submission Deadline:** November 4, 2026  
**Prize Pool:** $1,000,000  

---

## 📌 Basic Information

- **Project Title:** OmniDirector AI
- **Tagline / One-Liner (100 characters max):**  
  *Autonomous multimodal broadcast director & kinetic 9:16 vertical reel editor powered by Meta AI.*
- **Track:** Indie Developer Track
- **Theme:** Build for Your World (also applicable to Push the Frontier)
- **Repository URL:** [https://github.com/BishtNikhil/omnidirector-ai](https://github.com/BishtNikhil/omnidirector-ai)
- **Live Demo / Web Dashboard URL:** [http://localhost:8000](http://localhost:8000) (Self-hosted or Dockerized)
- **Primary Contact:** Nikhil Singh Bisht (`nikhilbisht.301@gmail.com`)
- **LinkedIn:** [https://www.linkedin.com/in/nikhil-singh-bisht/](https://www.linkedin.com/in/nikhil-singh-bisht/)
- **GitHub:** [https://github.com/BishtNikhil](https://github.com/BishtNikhil)

---

## 💡 Inspiration & Problem Statement

Independent creators, podcasters, livestreamers, and educators are trapped in a high-friction production bottleneck:
1. **Expensive Human Crews:** A professional 4-camera broadcast typically requires a Technical Director ($500–$1,500/day) to switch camera angles live, plus a video editor spending 8–15 hours post-stream slicing horizontal video into vertical 9:16 clips for TikTok, Instagram Reels, and YouTube Shorts.
2. **Clumsy Existing Automation:** Current automated multi-cam switchers rely solely on simple audio decibel gates. They trigger frantic, jarring cuts when someone coughs or laughs, have zero understanding of conversational pacing, and completely lack awareness of camera hardware connectivity.
3. **Manual Reel Framing:** When converting 16:9 widescreen video to 9:16 vertical format, static center-cropping frequently cuts off the speaker or leaves guests entirely out of frame.

We built **OmniDirector AI** to democratize high-end broadcast television production for solo creators worldwide. It acts as an autonomous virtual director in your browser—listening, watching, pacing narrative cuts, tracking subjects with sub-pixel computer vision, and producing ready-to-publish vertical highlight reels simultaneously.

---

## 🛠️ What It Does

1. **Autonomous Multi-Camera Directing (Meta Muse Spark & Muse Spark Open):**
   - Continuously evaluates a 4-camera matrix (Host Prime, Studio Wide, Screen/HUD, Reaction Cam).
   - Enforces a professional pacing engine (minimum 2.5s hold duration, maximum 12.0s refresh) to eliminate frantic micro-switching.
   - Arbitrates cuts based on speaker cadence, dialogue beats, and dramatic punchlines.
   - Integrates hardware-aware offline protection: Automatically locks to active cameras and skips disconnected or offline feeds.

2. **Zero-Shot Spatio-Temporal Segmentation (Meta SAM 3.1):**
   - Interactive Click-to-Track: Users can click any person, facial feature, or object on the live broadcast stage to send a point prompt to SAM 3.1.
   - Extracts polygonal contour boundaries in <15ms, enabling dynamic subject tracking without green screens.

3. **Kinetic 9:16 Vertical Reel Synthesis (Spring-Damped Physics):**
   - Employs real-time computer vision (native browser FaceDetector + skin-luminance centroid tracking) to continuously center-stage whoever is speaking.
   - Uses spring-damped physical easing (`0.08` coefficient) to smoothly glide the 9:16 viewport across widescreen video without jarring camera shakes.
   - 1-Click Export: Records 10-second VP9 WebM vertical highlight reels with synchronized karaoke captions.

4. **Professional Post-Production Integration (CMX 3600 EDL):**
   - 1-Click export of industry-standard Edit Decision Lists (EDL) with non-drop-frame timecodes, allowing editors to import all live cuts directly into DaVinci Resolve Studio and Adobe Premiere Pro.

5. **Multi-Cloud Scalable Architecture:**
   - 1-Click dynamic switching between **Baseten Serverless** (Meta Muse Spark Open, 2,000,000 TPM rate limit) and **Meta Model API Cloud** ($150 balance on `dev.meta.ai`), backed by a deterministic local simulation fallback.

---

## 🧠 Meta Models & Technologies Used

| Meta Model / Technology | Implementation in OmniDirector AI |
| :--- | :--- |
| **Meta Muse Spark Open** (`meta-models/muse-spark-open-1026`) | Primary autonomous director engine running on Baseten's serverless infrastructure with 2M TPM quota, arbitrating narrative cuts and generating directorial notes. |
| **Meta Muse Spark Cloud** (`muse-spark-1.1`) | Production cloud reasoning fallback running via Meta Model API (`https://api.meta.ai/v1`). |
| **Meta SAM 3.1** (Segment Anything) | Spatio-temporal object, subject, and HUD boundary contour extraction with interactive point prompt coordinates. |
| **Meta Muse Voice Transcribe** | Speech diarization, word-level timestamps, energy scoring, and climax/humor detection. |

---

## 🏗️ Architecture & Tech Stack

- **Backend:** Python 3.12, FastAPI, Uvicorn (ASGI), Pydantic v2, HTTPX (async client), WebSockets.
- **Frontend:** Vanilla HTML5 & CSS3 design system (Scandi-modern alabaster palette, Inter & JetBrains Mono typography, dark/light theme toggle, zero bloated frameworks).
- **Computer Vision:** HTML5 2D Canvas rendering engine, Native Browser FaceDetector API, Real-Time Centroid Skin-Luminance Tracking.
- **Export Formats:** CMX 3600 EDL (DaVinci/Premiere), WebM VP9 (9:16 Vertical Video).
- **DevOps:** Docker, Docker Compose, GitHub Actions.

---

## 🏆 Accomplishments We're Proud Of

1. **Sub-50ms Director Latency:** Achieved real-time directorial arbitration using Baseten's 2M TPM serverless infrastructure combined with WebSocket streaming.
2. **Spring-Damped Kinetic Physics:** Created a jitter-free, natural camera glide for 9:16 vertical re-framing that feels like an experienced human Steadicam operator.
3. **True Hardware Resilience:** Solved the common autonomous switcher bug where empty or off-air cameras get selected. OmniDirector AI queries stream readiness before making any cut.
4. **Complete Independence from Heavy Frameworks:** Built a clean, ultra-responsive 60 FPS studio interface using lightweight vanilla web technologies that loads instantly on any device.

---

## 🔮 What's Next for OmniDirector AI

- **Direct NDI & DeckLink Hardware Support:** Ingest uncompressed SDI/NDI feeds from professional broadcast cameras.
- **Automated Social Publishing:** Automatic multi-platform export to TikTok, Instagram Reels, and YouTube Shorts APIs immediately after the broadcast wraps.
- **Voiceover Commentary Agent:** Using Meta's generative audio models to dynamically insert live AI color-commentary or automated multi-language translation streams.
