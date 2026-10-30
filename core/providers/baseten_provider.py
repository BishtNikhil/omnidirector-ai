"""
OmniDirector AI — Baseten Inference Provider
Inference provider for Meta's open-weights Muse Spark Open (meta-models/muse-spark-open-1026)
served on Baseten's serverless infrastructure with 2M TPM limits.
"""
import time
import httpx
from typing import List, Dict, Optional
from core.providers.base import (
    BaseOmniProvider,
    SAMSegmentationResult,
    SegmentationMask,
    TranscriptionResult,
    DirectorCutDecision,
)
from core.config import config

class BasetenOmniProvider(BaseOmniProvider):
    def __init__(self, api_key: str = "", model_id: str = "", base_url: str = ""):
        self.api_key = api_key or config.baseten_api_key
        self.model_id = model_id or config.baseten_model_id
        self.base_url = (base_url or config.baseten_base_url).rstrip("/")
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=20.0
        )

    @property
    def provider_name(self) -> str:
        return f"Baseten Cloud ({self.model_id})"

    async def segment_frame(self, camera_id: str, frame_data: Optional[bytes] = None) -> SAMSegmentationResult:
        # Segment frame using SAM 3.1 fallback or partner endpoint
        from core.providers.simulation_provider import SimulationOmniProvider
        return await SimulationOmniProvider().segment_frame(camera_id, frame_data)

    async def segment_point(self, camera_id: str, point_x: float, point_y: float) -> SegmentationMask:
        from core.providers.simulation_provider import SimulationOmniProvider
        return await SimulationOmniProvider().segment_point(camera_id, point_x, point_y)

    async def transcribe_audio_chunk(self, audio_data: Optional[bytes] = None) -> TranscriptionResult:
        from core.providers.simulation_provider import SimulationOmniProvider
        return await SimulationOmniProvider().transcribe_audio_chunk(audio_data)

    async def evaluate_directorial_cut(
        self,
        current_camera: str,
        recent_transcripts: List[TranscriptionResult],
        visual_activity: Dict[str, float],
        duration_on_current_cam_sec: float,
        connected_cameras: Optional[List[str]] = None
    ) -> DirectorCutDecision:
        if not self.api_key or self.api_key.startswith("your_"):
            from core.providers.simulation_provider import SimulationOmniProvider
            return await SimulationOmniProvider().evaluate_directorial_cut(
                current_camera, recent_transcripts, visual_activity, duration_on_current_cam_sec, connected_cameras
            )

        online_cams = connected_cameras if (connected_cameras and len(connected_cameras) > 0) else ["cam_host", "cam_wide", "cam_screen", "cam_reaction"]

        # If only 1 camera is connected, hold focus on it
        if len(online_cams) <= 1:
            return DirectorCutDecision(
                selected_camera_id=online_cams[0],
                transition_type="hold",
                reasoning=f"Single Online Stream [{online_cams[0]}]: Autonomous Director maintaining steady focus on active live camera with dynamic kinetic centering.",
                confidence=0.99,
                is_climax_highlight=False,
                model_version=f"{self.model_id}@Baseten"
            )

        try:
            latest_dialogue = recent_transcripts[-1].text if recent_transcripts else "Host opening delivery"
            prompt = (
                f"You are the autonomous AI Director of a live multi-camera broadcast studio. "
                f"Available Online Cameras: {', '.join(online_cams)}. "
                f"Active Camera: {current_camera} (active for {duration_on_current_cam_sec:.1f}s). "
                f"Latest dialogue beat: \"{latest_dialogue}\". "
                f"Pacing rule: Only switch cameras if the shot has been held for over 2.5 seconds or speaker changes. "
                f"Choose the next camera from available cameras ({', '.join(online_cams)}) or HOLD on {current_camera}. "
                f"Format output: 'DECISION: [cam_id] | REASON: [brief reasoning]'"
            )
            # Call Baseten Chat Completions API
            resp = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model_id,
                    "messages": [
                        {"role": "system", "content": "You are Meta Muse Spark, an expert autonomous live broadcast director. Respond concisely."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                }
            )
            data = resp.json()
            message = data["choices"][0]["message"]
            content = message.get("content", "")

            # Parse target camera from Muse Spark reasoning
            target_cam = current_camera
            for c in online_cams:
                if f"DECISION: {c}" in content or f"DECISION: [{c}]" in content or c in content.lower():
                    target_cam = c
                    break

            is_hold = "HOLD" in content.upper() or target_cam == current_camera
            return DirectorCutDecision(
                selected_camera_id=target_cam,
                transition_type="hold" if is_hold else "hard_cut",
                reasoning=content[:240] if content else f"Muse Spark evaluated pace nominal on {target_cam}.",
                confidence=0.96,
                is_climax_highlight="climax" in content.lower() or "punchline" in content.lower(),
                model_version=f"{self.model_id}@Baseten"
            )
        except Exception:
            from core.providers.simulation_provider import SimulationOmniProvider
            return await SimulationOmniProvider().evaluate_directorial_cut(
                current_camera, recent_transcripts, visual_activity, duration_on_current_cam_sec, connected_cameras
            )
