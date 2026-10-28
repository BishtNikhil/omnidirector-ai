"""
OmniDirector AI — High-Fidelity Simulation Provider
Provides zero-downtime, sub-second realistic studio stream simulation,
SAM 3.1 polygonal segmentation tracking, and Muse Spark reasoning traces.
"""
import time
import random
import math
from typing import List, Dict, Optional
from core.providers.base import (
    BaseOmniProvider,
    SAMSegmentationResult,
    SegmentationMask,
    TranscriptionResult,
    TranscriptionWord,
    DirectorCutDecision,
)

SAMPLE_DIALOGUE_STREAM = [
    {
        "speaker": "host",
        "text": "Welcome back to the live build session! Today we are testing Meta's frontier Muse models.",
        "energy": 0.65,
        "emotions": ["engaged", "confident"],
        "climax": False,
        "suggested_cam": "cam_host"
    },
    {
        "speaker": "host",
        "text": "Take a look at this real-time inference latency graph on the center monitor.",
        "energy": 0.72,
        "emotions": ["enthusiastic", "focused"],
        "climax": False,
        "suggested_cam": "cam_screen"
    },
    {
        "speaker": "guest",
        "text": "Wait, are you telling me SAM 3.1 is segmenting the entire HUD in under sixteen milliseconds?!",
        "energy": 0.88,
        "emotions": ["amazed", "surprised"],
        "climax": True,
        "suggested_cam": "cam_reaction"
    },
    {
        "speaker": "host",
        "text": "Exactly. Sub-pixel boundaries with zero green-screen requirement. That's the power of Meta AI.",
        "energy": 0.94,
        "emotions": ["triumphant", "intense"],
        "climax": True,
        "suggested_cam": "cam_wide"
    },
    {
        "speaker": "host",
        "text": "Notice how the kinetic 9:16 vertical engine automatically centers our faces while preserving the live gameplay.",
        "energy": 0.78,
        "emotions": ["educational", "articulate"],
        "climax": False,
        "suggested_cam": "cam_host"
    },
    {
        "speaker": "guest",
        "text": "This completely replaces five hours of manual Premiere Pro keyframing and rotoscoping.",
        "energy": 0.82,
        "emotions": ["impressed", "relieved"],
        "climax": False,
        "suggested_cam": "cam_reaction"
    }
]

class SimulationOmniProvider(BaseOmniProvider):
    def __init__(self):
        self._step = 0
        self._start_time = time.time()

    @property
    def provider_name(self) -> str:
        return "Simulation-Local-Fallback (Pre-Credit Standby)"

    async def segment_frame(self, camera_id: str, frame_data: Optional[bytes] = None) -> SAMSegmentationResult:
        t0 = time.time()
        # Generate organic oscillating polygon points for SAM 3.1 simulation
        t = time.time() - self._start_time
        dx = math.sin(t * 1.5) * 0.02
        dy = math.cos(t * 1.2) * 0.015

        if camera_id == "cam_host":
            # Primary host face & microphone segmentation
            masks = [
                SegmentationMask(
                    id="host_portrait",
                    label="Host (Primary Subject)",
                    confidence=0.982,
                    bounding_box=[0.32 + dx, 0.18 + dy, 0.68 + dx, 0.88 + dy],
                    polygon_points=[
                        [0.48 + dx, 0.18 + dy], [0.60 + dx, 0.28 + dy], [0.66 + dx, 0.50 + dy],
                        [0.64 + dx, 0.75 + dy], [0.55 + dx, 0.88 + dy], [0.42 + dx, 0.88 + dy],
                        [0.34 + dx, 0.75 + dy], [0.32 + dx, 0.50 + dy], [0.38 + dx, 0.28 + dy]
                    ],
                    suggested_crop_x=0.50 + dx
                ),
                SegmentationMask(
                    id="host_mic",
                    label="Shure SM7B Mic",
                    confidence=0.941,
                    bounding_box=[0.24, 0.55, 0.36, 0.78],
                    polygon_points=[
                        [0.26, 0.55], [0.34, 0.57], [0.36, 0.72], [0.28, 0.78], [0.24, 0.68]
                    ],
                    suggested_crop_x=0.50
                )
            ]
        elif camera_id == "cam_screen":
            # HUD, Code editor, and Telemetry graph segmentation
            masks = [
                SegmentationMask(
                    id="hud_telemetry",
                    label="Live Inference Telemetry Panel",
                    confidence=0.965,
                    bounding_box=[0.05, 0.08, 0.45, 0.45],
                    polygon_points=[
                        [0.05, 0.08], [0.45, 0.08], [0.45, 0.45], [0.05, 0.45]
                    ],
                    suggested_crop_x=0.25
                ),
                SegmentationMask(
                    id="code_editor",
                    label="Meta Model API Code Window",
                    confidence=0.978,
                    bounding_box=[0.48, 0.10, 0.95, 0.90],
                    polygon_points=[
                        [0.48, 0.10], [0.95, 0.10], [0.95, 0.90], [0.48, 0.90]
                    ],
                    suggested_crop_x=0.70
                )
            ]
        elif camera_id == "cam_reaction":
            # Guest profile segmentation
            masks = [
                SegmentationMask(
                    id="guest_profile",
                    label="Guest Profile (Active Reaction)",
                    confidence=0.962,
                    bounding_box=[0.28 - dx, 0.22 - dy, 0.72 - dx, 0.90 - dy],
                    polygon_points=[
                        [0.45 - dx, 0.22 - dy], [0.65 - dx, 0.32 - dy], [0.72 - dx, 0.60 - dy],
                        [0.60 - dx, 0.90 - dy], [0.35 - dx, 0.90 - dy], [0.28 - dx, 0.60 - dy]
                    ],
                    suggested_crop_x=0.50 - dx
                )
            ]
        else:
            # Wide studio master table segmentation
            masks = [
                SegmentationMask(
                    id="studio_podium",
                    label="Studio Broadcast Table",
                    confidence=0.951,
                    bounding_box=[0.15, 0.60, 0.85, 0.95],
                    polygon_points=[
                        [0.15, 0.65], [0.85, 0.65], [0.88, 0.95], [0.12, 0.95]
                    ],
                    suggested_crop_x=0.50
                )
            ]

        latency = (time.time() - t0) * 1000 + random.uniform(11.2, 14.8)
        return SAMSegmentationResult(
            timestamp_ms=time.time() * 1000,
            model_version="Meta-SAM-3.1-LocalSim",
            masks=masks,
            latency_ms=round(latency, 2)
        )

    async def segment_point(self, camera_id: str, point_x: float, point_y: float) -> SegmentationMask:
        """Simulate Meta SAM 3.1 zero-shot point prompt segmentation at (x, y)."""
        rx = random.uniform(0.06, 0.10)
        ry = random.uniform(0.08, 0.13)
        # Create an 8-sided polygon surrounding the click point
        pts = []
        for i in range(8):
            angle = (i / 8) * math.pi * 2
            jitter = random.uniform(0.85, 1.15)
            px = max(0.01, min(0.99, point_x + math.cos(angle) * rx * jitter))
            py = max(0.01, min(0.99, point_y + math.sin(angle) * ry * jitter))
            pts.append([round(px, 3), round(py, 3)])

        return SegmentationMask(
            id=f"sam_point_{int(time.time() * 1000)}",
            label=f"SAM 3.1 Focus ({point_x:.2f}, {point_y:.2f})",
            confidence=round(random.uniform(0.965, 0.992), 3),
            bounding_box=[
                max(0.0, point_x - rx), max(0.0, point_y - ry),
                min(1.0, point_x + rx), min(1.0, point_y + ry)
            ],
            polygon_points=pts,
            suggested_crop_x=point_x
        )

    async def transcribe_audio_chunk(self, audio_data: Optional[bytes] = None) -> TranscriptionResult:
        # Rotate through dialogue beats
        item = SAMPLE_DIALOGUE_STREAM[self._step % len(SAMPLE_DIALOGUE_STREAM)]
        self._step += 1
        
        words_raw = item["text"].split()
        now = time.time() * 1000
        words = []
        cur_ms = now
        for w in words_raw:
            dur = len(w) * 45 + random.uniform(30, 80)
            words.append(TranscriptionWord(
                word=w,
                start_ms=round(cur_ms, 1),
                end_ms=round(cur_ms + dur, 1),
                confidence=round(random.uniform(0.96, 0.99), 3),
                speaker_id=item["speaker"]
            ))
            cur_ms += dur + 25

        return TranscriptionResult(
            timestamp_ms=now,
            text=item["text"],
            speaker_id=item["speaker"],
            is_climax_moment=item["climax"],
            energy_score=item["energy"],
            detected_emotions=item["emotions"],
            words=words,
            model_version="Meta-Muse-Voice-Transcribe-LocalSim"
        )

    async def evaluate_directorial_cut(
        self,
        current_camera: str,
        recent_transcripts: List[TranscriptionResult],
        visual_activity: Dict[str, float],
        duration_on_current_cam_sec: float,
        connected_cameras: Optional[List[str]] = None
    ) -> DirectorCutDecision:
        latest = recent_transcripts[-1] if recent_transcripts else None
        
        # Determine online cameras
        online_cams = connected_cameras if (connected_cameras and len(connected_cameras) > 0) else ["cam_host", "cam_wide", "cam_screen", "cam_reaction"]

        # Ensure current camera is valid
        if current_camera not in online_cams:
            current_camera = online_cams[0]

        # If only 1 camera is connected (e.g. Host Webcam), NEVER cut away to offline feeds!
        if len(online_cams) <= 1:
            return DirectorCutDecision(
                selected_camera_id=online_cams[0],
                transition_type="hold",
                reasoning=f"Single Online Feed [{online_cams[0]}]: Autonomous Director maintaining steady focus on active live camera with dynamic kinetic centering.",
                confidence=0.99,
                is_climax_highlight=False,
                model_version="Meta-Muse-Spark-LocalSim"
            )

        # Guard minimum cut interval (e.g. 2.5s) to prevent jarring cuts
        if duration_on_current_cam_sec < 2.5:
            return DirectorCutDecision(
                selected_camera_id=current_camera,
                transition_type="hold",
                reasoning=f"Hold on {current_camera}: current shot duration ({duration_on_current_cam_sec:.1f}s) has not exceeded minimum pacing threshold (2.5s).",
                confidence=0.92,
                is_climax_highlight=False,
                model_version="Meta-Muse-Spark-LocalSim"
            )

        # Climax moment detection: Switch to wide or reaction if online
        if latest and latest.is_climax_moment:
            for cand in ["cam_wide", "cam_reaction", "cam_host"]:
                if cand in online_cams and cand != current_camera:
                    return DirectorCutDecision(
                        selected_camera_id=cand,
                        transition_type="smooth_dissolve",
                        reasoning=f"High vocal energy detected ({latest.energy_score:.2f}) with emotions {latest.detected_emotions}. Cutting to online {cand} to frame full conversational dynamic.",
                        confidence=0.97,
                        is_climax_highlight=True,
                        model_version="Meta-Muse-Spark-LocalSim"
                    )

        # Speaker handoff logic: only switch to reaction if reaction cam is connected/online!
        if latest and latest.speaker_id == "guest" and "cam_reaction" in online_cams and current_camera != "cam_reaction":
            return DirectorCutDecision(
                selected_camera_id="cam_reaction",
                transition_type="hard_cut",
                reasoning="Muse Voice Transcribe identified speaker shift to 'guest'. Shifting active framing to Reaction Camera.",
                confidence=0.95,
                is_climax_highlight=False,
                model_version="Meta-Muse-Spark-LocalSim"
            )
        
        # Screen activity logic: only switch to screen if screen cam is connected/online!
        screen_activity = visual_activity.get("cam_screen", 0.0)
        if screen_activity > 0.65 and "cam_screen" in online_cams and current_camera != "cam_screen":
            return DirectorCutDecision(
                selected_camera_id="cam_screen",
                transition_type="hard_cut",
                reasoning="Vision Sentinel detected rapid motion/UI updates on screen (activity score 0.78). Switching to Screen/HUD feed.",
                confidence=0.91,
                is_climax_highlight=False,
                model_version="Meta-Muse-Spark-LocalSim"
            )

        # Natural rhythm refresh if held too long (> 9.0s) among available online cameras
        if duration_on_current_cam_sec > 9.0:
            other_cams = [c for c in online_cams if c != current_camera]
            if other_cams:
                target = other_cams[0]
                return DirectorCutDecision(
                    selected_camera_id=target,
                    transition_type="smooth_dissolve",
                    reasoning=f"Shot duration on {current_camera} exceeded 9.0s. Refreshing perspective to online camera {target}.",
                    confidence=0.88,
                    is_climax_highlight=False,
                    model_version="Meta-Muse-Spark-LocalSim"
                )

        # Default hold
        return DirectorCutDecision(
            selected_camera_id=current_camera,
            transition_type="hold",
            reasoning=f"Pacing nominal on active camera {current_camera}. Host delivery steady.",
            confidence=0.90,
            is_climax_highlight=False,
            model_version="Meta-Muse-Spark-LocalSim"
        )
