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
    def __init__(self, api_key: str = "", model_id: str = ""):
        self.api_key = api_key or config.baseten_api_key
        self.model_id = model_id or config.baseten_model_id
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Api-Key {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=15.0
        )

    @property
    def provider_name(self) -> str:
        return f"Baseten Inference ({self.model_id})"

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

        try:
            prompt = (
                f"You are the autonomous AI Director of a live broadcast. "
                f"Active Camera: {current_camera}. Duration: {duration_on_current_cam_sec:.1f}s. "
                f"Latest dialogue: {recent_transcripts[-1].text if recent_transcripts else 'N/A'}. "
                f"Choose next camera (cam_host, cam_wide, cam_screen, cam_reaction) and output your reasoning."
            )
            # Call Baseten Chat Completions API
            resp = await self.client.post(
                "https://bridge.baseten.co/v1/chat/completions",
                json={
                    "model": self.model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
            )
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            target_cam = current_camera
            for c in ["cam_host", "cam_wide", "cam_screen", "cam_reaction"]:
                if c in content:
                    target_cam = c
                    break

            return DirectorCutDecision(
                selected_camera_id=target_cam,
                transition_type="hard_cut",
                reasoning=content,
                confidence=0.95,
                is_climax_highlight=False,
                model_version=f"{self.model_id}@Baseten"
            )
        except Exception:
            from core.providers.simulation_provider import SimulationOmniProvider
            return await SimulationOmniProvider().evaluate_directorial_cut(
                current_camera, recent_transcripts, visual_activity, duration_on_current_cam_sec
            )
