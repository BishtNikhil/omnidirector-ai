"""
OmniDirector AI — Chief Autonomous Director Agent
Coordinates multimodal perception, camera matrix arbitration,
kinetic pan-and-scan framing, and highlight bookmarking.
"""
import time
import asyncio
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from core.config import config
from core.providers import get_active_provider
from core.providers.base import (
    BaseOmniProvider,
    DirectorCutDecision,
    SAMSegmentationResult,
    TranscriptionResult
)

class StreamTelemetry(BaseModel):
    active_camera_id: str
    active_camera_label: str
    time_on_camera_sec: float
    total_cuts_made: int
    is_auto_directing: bool = True
    active_provider_name: str
    latest_decision: Optional[DirectorCutDecision] = None
    latest_transcription: Optional[TranscriptionResult] = None
    latest_sam_segmentation: Optional[SAMSegmentationResult] = None
    kinetic_crop_x: float = 0.5
    kinetic_crop_y: float = 0.5
    climax_highlights_count: int = 0
    recent_cuts_history: List[Dict[str, Any]] = Field(default_factory=list)
    connected_cameras: List[str] = Field(default_factory=list)

class DirectorAgent:
    def __init__(self, provider: Optional[BaseOmniProvider] = None):
        self.provider = provider or get_active_provider()
        self.connected_cameras: List[str] = [c.id for c in config.cameras if getattr(c, 'is_connected', True)]
        self.active_camera = self.connected_cameras[0] if self.connected_cameras else "cam_host"
        self.last_cut_timestamp = time.time()
        self.total_cuts = 0
        self.is_auto_directing = True
        self.manual_override_until = 0.0
        
        self.recent_transcripts: List[TranscriptionResult] = []
        self.recent_cuts: List[Dict[str, Any]] = []
        self.highlights: List[Dict[str, Any]] = []
        
        self.visual_activity: Dict[str, float] = {
            "cam_host": 0.5,
            "cam_wide": 0.3,
            "cam_screen": 0.2,
            "cam_reaction": 0.4
        }
        
        self.kinetic_x = 0.5
        self.kinetic_y = 0.5
        self.latest_decision: Optional[DirectorCutDecision] = None
        self.latest_sam: Optional[SAMSegmentationResult] = None

    def get_camera_label(self, cam_id: str) -> str:
        for c in config.cameras:
            if c.id == cam_id:
                return c.label
        return cam_id

    def manual_cut(self, camera_id: str, lock_duration_sec: float = 6.0) -> DirectorCutDecision:
        """Manual director intervention overrides AI for lock_duration_sec."""
        prev = self.active_camera
        self.active_camera = camera_id
        self.last_cut_timestamp = time.time()
        self.total_cuts += 1
        self.manual_override_until = time.time() + lock_duration_sec
        
        decision = DirectorCutDecision(
            selected_camera_id=camera_id,
            transition_type="hard_cut",
            reasoning=f"Manual Creator Override: Director switched from {prev} to {camera_id}. AI locked for {lock_duration_sec}s.",
            confidence=1.0,
            is_climax_highlight=False,
            model_version="Human-in-the-Loop Override"
        )
        self.latest_decision = decision
        self.recent_cuts.append({
            "timestamp": time.strftime("%H:%M:%S"),
            "camera": self.get_camera_label(camera_id),
            "reason": decision.reasoning,
            "type": "Manual"
        })
        return decision

    def set_camera_status(self, camera_id: str, is_connected: bool) -> List[str]:
        """Toggles a camera's online/offline connectivity in the multi-camera matrix."""
        for c in config.cameras:
            if c.id == camera_id:
                c.is_connected = is_connected

        if is_connected:
            if camera_id not in self.connected_cameras:
                self.connected_cameras.append(camera_id)
        else:
            if camera_id in self.connected_cameras:
                self.connected_cameras.remove(camera_id)
            if self.active_camera == camera_id and self.connected_cameras:
                self.active_camera = self.connected_cameras[0]
                self.last_cut_timestamp = time.time()
                self.total_cuts += 1
                self.recent_cuts.insert(0, {
                    "timestamp": time.strftime("%H:%M:%S"),
                    "camera": self.get_camera_label(self.active_camera),
                    "reason": f"Signal lost on {camera_id}. Emergency failover to online camera.",
                    "type": "Emergency Failover"
                })

        return self.connected_cameras

    async def step(self) -> StreamTelemetry:
        """Single heartbeat cycle of the autonomous director."""
        now = time.time()

        # Enforce that active camera is an online camera
        if self.connected_cameras and self.active_camera not in self.connected_cameras:
            self.active_camera = self.connected_cameras[0]
            self.last_cut_timestamp = now

        duration_on_cam = now - self.last_cut_timestamp

        # 1. Perception: Ingest audio transcript beat
        transcript = await self.provider.transcribe_audio_chunk()
        self.recent_transcripts.append(transcript)
        if len(self.recent_transcripts) > 10:
            self.recent_transcripts.pop(0)

        # 2. Perception: SAM 3.1 Segmentation on active camera
        self.latest_sam = await self.provider.segment_frame(self.active_camera)

        # Smoothly track kinetic crop center towards highest confidence subject mask
        if self.latest_sam and self.latest_sam.masks:
            target_x = self.latest_sam.masks[0].suggested_crop_x
            # Smooth exponential moving average for jitter-free cinematic pan
            self.kinetic_x = self.kinetic_x * 0.75 + target_x * 0.25

        # 3. Decision: If manual override lock has expired, evaluate AI directorial arbitration
        if now >= self.manual_override_until and self.is_auto_directing:
            decision = await self.provider.evaluate_directorial_cut(
                current_camera=self.active_camera,
                recent_transcripts=self.recent_transcripts,
                visual_activity=self.visual_activity,
                duration_on_current_cam_sec=duration_on_cam,
                connected_cameras=self.connected_cameras
            )
            self.latest_decision = decision

            # Enforce that AI cannot cut to an offline camera
            target_cam = decision.selected_camera_id
            if target_cam in self.connected_cameras and target_cam != self.active_camera and decision.transition_type != "hold":
                prev_cam = self.active_camera
                self.active_camera = target_cam
                self.last_cut_timestamp = now
                self.total_cuts += 1
                
                cut_record = {
                    "timestamp": time.strftime("%H:%M:%S"),
                    "camera": self.get_camera_label(self.active_camera),
                    "reason": decision.reasoning,
                    "type": decision.transition_type,
                    "model": decision.model_version
                }
                self.recent_cuts.insert(0, cut_record)
                if len(self.recent_cuts) > 15:
                    self.recent_cuts.pop()

                if decision.is_climax_highlight:
                    self.highlights.append(cut_record)

        return StreamTelemetry(
            active_camera_id=self.active_camera,
            active_camera_label=self.get_camera_label(self.active_camera),
            time_on_camera_sec=round(time.time() - self.last_cut_timestamp, 1),
            total_cuts_made=self.total_cuts,
            is_auto_directing=self.is_auto_directing,
            active_provider_name=self.provider.provider_name,
            latest_decision=self.latest_decision,
            latest_transcription=self.recent_transcripts[-1] if self.recent_transcripts else None,
            latest_sam_segmentation=self.latest_sam,
            kinetic_crop_x=round(self.kinetic_x, 3),
            kinetic_crop_y=round(self.kinetic_y, 3),
            climax_highlights_count=len(self.highlights),
            recent_cuts_history=self.recent_cuts[:6],
            connected_cameras=list(self.connected_cameras)
        )

# Global Director Instance
director = DirectorAgent()
