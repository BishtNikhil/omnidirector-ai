"""
OmniDirector AI — Base Model Provider Specification
Abstract interfaces for Meta Model API, Baseten, and Local Simulation Fallbacks.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time

class SegmentationMask(BaseModel):
    id: str
    label: str  # e.g., 'host_face', 'guest_body', 'game_hud', 'microphone'
    confidence: float
    polygon_points: List[List[float]] = Field(default_factory=list, description="Normalized [x, y] coordinates 0.0-1.0")
    bounding_box: List[float] = Field(default_factory=list, description="[x_min, y_min, x_max, y_max]")
    suggested_crop_x: float = 0.5  # Optimal center for 9:16 vertical framing

class SAMSegmentationResult(BaseModel):
    timestamp_ms: float
    model_version: str = "Meta-SAM-3.1"
    masks: List[SegmentationMask]
    latency_ms: float

class TranscriptionWord(BaseModel):
    word: str
    start_ms: float
    end_ms: float
    confidence: float
    speaker_id: str

class TranscriptionResult(BaseModel):
    timestamp_ms: float
    text: str
    speaker_id: str
    is_climax_moment: bool = False
    energy_score: float = 0.5  # 0.0 to 1.0
    detected_emotions: List[str] = Field(default_factory=list)
    words: List[TranscriptionWord] = Field(default_factory=list)
    model_version: str = "Meta-Muse-Voice-Transcribe"

class DirectorCutDecision(BaseModel):
    timestamp_ms: float = Field(default_factory=lambda: time.time() * 1000)
    selected_camera_id: str
    transition_type: str = "hard_cut"  # hard_cut, smooth_dissolve, split_screen, pip_hud
    reasoning: str
    confidence: float
    kinetic_crop_x: float = 0.5
    kinetic_crop_y: float = 0.5
    is_climax_highlight: bool = False
    model_version: str = "Meta-Muse-Spark"

class BaseOmniProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def segment_frame(self, camera_id: str, frame_data: Optional[bytes] = None) -> SAMSegmentationResult:
        """Run Meta SAM 3.1 spatio-temporal segmentation on video frame."""
        pass

    @abstractmethod
    async def transcribe_audio_chunk(self, audio_data: Optional[bytes] = None) -> TranscriptionResult:
        """Run Meta Muse Voice Transcribe on incoming audio chunk."""
        pass

    @abstractmethod
    async def evaluate_directorial_cut(
        self,
        current_camera: str,
        recent_transcripts: List[TranscriptionResult],
        visual_activity: Dict[str, float],
        duration_on_current_cam_sec: float
    ) -> DirectorCutDecision:
        """Run Meta Muse Spark reasoning to arbitrate optimal camera switch."""
        pass
