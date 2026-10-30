"""
OmniDirector AI — Core Configuration & Environment Matrix
"""
import os
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load local .env credentials
load_dotenv()

class CameraDefinition(BaseModel):
    id: str
    label: str
    role: str  # host, wide, screen, reaction
    fov_degrees: int = 75
    resolution: str = "1080p60"
    description: str
    is_connected: bool = True

class DirectorPolicy(BaseModel):
    min_cut_duration_sec: float = Field(default=2.5, description="Prevent frantic micro-switching")
    max_cut_duration_sec: float = Field(default=12.0, description="Force dynamic perspective refresh")
    climax_energy_threshold: float = Field(default=0.75, description="Triggers dynamic multi-cam split")
    speech_hold_lead_time_ms: int = Field(default=350, description="Lead camera before speaker finishes sentence")
    auto_kinetic_vertical_crop: bool = True

class OmniConfig(BaseModel):
    app_name: str = "OmniDirector AI Studio"
    version: str = "1.0.0"
    port: int = int(os.getenv("OMNIDIRECTOR_PORT", "8000"))
    environment: str = os.getenv("OMNIDIRECTOR_ENV", "development")
    
    # Meta Model API
    meta_api_key: str = os.getenv("META_MODEL_API_KEY", "")
    meta_base_url: str = os.getenv("META_MODEL_BASE_URL", "https://api.meta.ai/v1")
    meta_model_name: str = os.getenv("META_MODEL_NAME", "muse-spark-1.1")
    
    # Baseten Inference (Muse Spark Open)
    baseten_api_key: str = os.getenv("BASETEN_API_KEY", "")
    baseten_base_url: str = os.getenv("BASETEN_BASE_URL", "https://inference.baseten.co/v1")
    baseten_model_id: str = os.getenv("BASETEN_MODEL_ID", "meta-models/muse-spark-open-1026")
    
    # Provider Selection
    primary_provider: str = os.getenv("DIRECTOR_PRIMARY_PROVIDER", "baseten")

    # Fallback Mode
    enable_simulation: bool = os.getenv("ENABLE_LOCAL_SIMULATION_FALLBACK", "true").lower() in ("true", "1", "yes")
    
    # Cameras
    cameras: List[CameraDefinition] = [
        CameraDefinition(
            id="cam_host",
            label="CAM 1 — Host Prime",
            role="host",
            fov_degrees=50,
            resolution="1080p60",
            description="Primary host close-up portrait with shallow depth of field"
        ),
        CameraDefinition(
            id="cam_wide",
            label="CAM 2 — Studio Wide",
            role="wide",
            fov_degrees=90,
            resolution="1080p60",
            description="Master establishing shot capturing studio table, spatial lighting, and co-host"
        ),
        CameraDefinition(
            id="cam_screen",
            label="CAM 3 — Screen & HUD",
            role="screen",
            fov_degrees=0,
            resolution="1080p60",
            description="Direct display capture of application, gameplay, or slide deck"
        ),
        CameraDefinition(
            id="cam_reaction",
            label="CAM 4 — Reaction Cam",
            role="reaction",
            fov_degrees=65,
            resolution="1080p60",
            description="Dynamic side-profile tracking guest reactions, laughter, and interactions"
        ),
    ]
    
    policy: DirectorPolicy = DirectorPolicy()

config = OmniConfig()
