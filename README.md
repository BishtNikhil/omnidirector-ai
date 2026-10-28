# 🎬 OmniDirector AI — Autonomous Multimodal Broadcast & Spatial Stream Director

> **Official Submission for Meta Global AI Developer Hackathon 2026 ($1M Prize Pool)**  
> **Track:** Indie Developer Track  
> **Theme:** Build for Your World  
> **Lead Developer:** Nikhil Singh Bisht ([GitHub](https://github.com/BishtNikhil) • [LinkedIn](https://www.linkedin.com/in/nikhil-singh-bisht/))  
> **Repository:** [https://github.com/BishtNikhil/omnidirector-ai](https://github.com/BishtNikhil/omnidirector-ai)

---

## ⚡ The Vision: Autonomous Live Directing for the Creator Era

In modern live broadcasting, esports, podcasting, and creator workflows, producing high-fidelity multi-camera productions requires a team of human operators: a technical director switching cameras, a graphics operator managing lower-thirds, an audio engineer riding faders, and video editors spending 10+ hours slicing long-form multicam footage into 9:16 vertical reels.

**OmniDirector AI** eliminates this bottleneck. Powered by Meta's frontier generative and vision foundation models, OmniDirector acts as an autonomous virtual control room:
1. **Zero-Latency Multicam Switching**: Ingests multi-camera angles (Host, Wide, Screen/HUD, Guest) and dynamically cuts cameras based on speaker cadence, emotional intensity, and screen motion.
2. **Spatio-Temporal Subject Segmentation (SAM 3.1)**: Dynamically extracts subjects, facecams, game HUDs, and background layers in real time without green screens.
3. **Conversational Speech & Punchline Tracking (Muse Voice Transcribe)**: Detects sub-second word timestamps, silence pauses, jokes, and emotional climaxes.
4. **Autonomous Narrative Direction (Muse Spark & Muse Spark Open)**: Evaluates live stream state, predicts optimal narrative transitions, and triggers contextual b-roll and lower-thirds.
5. **Kinetic 9:16 Vertical Reel Synthesis**: Continuously tracks subjects across the 16:9 frame and generates crop-optimized vertical reels with synchronized karaoke subtitles.

---

## 🏛️ System Architecture

```text
                                 🎬 OMNIDIRECTOR AI CORE
                                            │
  ┌───────────────────────┬─────────────────┴─────────────────┬───────────────────────┐
  ▼                       ▼                                   ▼                       ▼
📹 MULTI-CAMERA STREAM   🎙️ AUDIO STREAM                     🧠 META REASONING CORE  🖼️ VISUAL SEGMENTATION
  4-Channel Video Ingest    Muse Voice Transcribe (Sub-Sec)     Muse Spark / Spark Open SAM 3.1 Zero-Shot
  (Cam1 / Cam2 / Cam3 / 4)  Cadence, Pauses & Climax Energy     Multi-Agent Director     Subject & HUD Masks
  └───────────┬───────────┴─────────────────┬─────────────────┴───────────┬───────────┘
              │                             │                             │
              ▼                             ▼                             ▼
       ┌────────────────────────────────────────────────────────────────────────┐
       │             🔱 MULTI-AGENT DIRECTORIAL ARBITRATION MESH                 │
       │  • Vision Sentinel: Analyzes gaze, movement, and visual energy         │
       │  • Cadence Auditor: Detects speech handoffs and speaker dominance      │
       │  • Kinetic Pacer: Decides cuts (Close-up, Wide, Split-screen, Overlay) │
       │  • Highlight Clipper: Marks high-engagement viral climax timestamps    │
       └───────────────────────────────────┬────────────────────────────────────┘
                                           │
                                           ▼
       ┌────────────────────────────────────────────────────────────────────────┐
       │             🚀 LIVE BROADCAST & KINETIC VERTICAL PIPELINE              │
       │  • Zero-Lag Glassmorphic Studio Dashboard (WAI-ARIA AAA)               │
       │  • Real-Time SAM 3.1 Interactive Mask Visualizer                       │
       │  • Automated 9:16 Kinetic Pan-and-Scan Engine (FFmpeg & Canvas)        │
       │  • Meta Model API & Baseten / Modal Serverless Inference Endpoints     │
       └────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Deep Integration of Meta Models & Tooling

OmniDirector AI is purpose-built to showcase Meta's generative and foundation AI ecosystem:

| Meta Model | Architectural Role in OmniDirector AI |
| :--- | :--- |
| **Meta Muse Spark** | The Chief Executive Director agent reasoning over multimodal stream metadata, pacing cuts, and generating situational director notes. |
| **Meta SAM 3.1 (Segment Anything)** | Zero-shot spatio-temporal segmentation of speakers, facecams, and UI HUDs for dynamic framing and green-screen-less background replacement. |
| **Meta Muse Voice Transcribe** | Sub-second word-level timestamping, speaker diarization, laughter/applause event detection, and real-time karaoke caption synchronization. |
| **Meta Muse Spark Open** | Deployed on Baseten & Modal for high-throughput, private serverless multi-agent reasoning with 2M TPM rate limits. |
| **Meta Muse Image / Wonder** | Dynamic generative background synthesis, thematic transition cards, and contextual lower-third visual overlays. |

---

## 🛡️ Zero-Downtime Pluggable Provider Architecture

To maintain 100% testability and zero downtime across any network environment, OmniDirector AI implements a decoupled **Model Adapter Protocol**:
- **Meta Model API Provider**: Direct production integration with `dev.meta.ai`.
- **Baseten Serverless Provider**: High-throughput execution of `meta-models/muse-spark-open-1026`.
- **Modal Endpoints Provider**: Serverless containerized GPU inference for SAM 3.1.
- **Local / Deterministic Fallback Engine**: Comprehensive offline simulation and deterministic heuristics that allow full end-to-end studio operation even when external cloud quotas or credentials are being provisioned.

---

## 💎 Commercial SaaS & Studio Features

OmniDirector AI incorporates production-grade broadcast engineering standards:
- **🎯 Interactive SAM 3.1 Click-to-Track**: Click directly on any subject or object on the 4K canvas to send a zero-shot coordinate point prompt to SAM 3.1, extracting sub-pixel polygonal boundaries in <15ms.
- **📱 Cinematic Spring-Damped Center-Staging**: Continuous pan-and-scan 9:16 vertical stream with physical spring damping (`0.08` coefficient) and active speaker lock HUD brackets (`TARGET: HOST (LOCKED)` / `TARGET: GUEST`).
- **🎬 CMX 3600 EDL Export**: 1-Click export of industry-standard Edit Decision Lists ready for DaVinci Resolve and Adobe Premiere Pro multicam timelines.
- **🔬 Meta Model Payloads & Architecture Transparency**: Slide-out live inspector displaying actual system prompts, reasoning schemas, and output contracts for Muse Spark, SAM 3.1, and Muse Voice Transcribe.
- **📹 Live Hardware & Virtual Ingest**: Seamlessly toggle between multi-cam synchronized feeds and live WebRTC camera/OBS Virtual Camera inputs.
- **🎨 Washed-Out Scandinavian Studio Aesthetic**: High-legibility Inter typography, muted alabaster palette (`#F6F7F9`), dual Light/Dark studio modes, and calibrated decibel VU meter waveforms.

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.10+ (Recommended: Python 3.12)
- Node.js 18+ (Optional for advanced asset tooling)
- Modern web browser (Chrome, Edge, Firefox, Brave)

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/BishtNikhil/omnidirector-ai.git
cd omnidirector-ai
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Keys
```bash
cp .env.example .env
# Fill in your META_MODEL_API_KEY, BASETEN_API_KEY, or MODAL_TOKEN
```

### 3. Launch OmniDirector Studio
```bash
python app.py
```
Open [http://localhost:8000](http://localhost:8000) to access the live glassmorphic control room.

---

## 📄 License
This project is licensed under the Apache 2.0 License — open source and free for the global developer community.
