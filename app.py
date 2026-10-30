"""
OmniDirector AI — Production FastAPI Server & Real-Time WebSocket Mesh
"""
import os
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from core.config import config
from core.agents.director_agent import director, StreamTelemetry
from core.providers import get_active_provider

# Background heartbeat task
heartbeat_task = None

async def broadcast_director_loop():
    """Continuous background perception & decision loop."""
    while True:
        try:
            await director.step()
            await asyncio.sleep(1.2)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Director Loop Error] {e}")
            await asyncio.sleep(2.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global heartbeat_task
    heartbeat_task = asyncio.create_task(broadcast_director_loop())
    print("[OmniDirector AI] Engine Initialized & Live Loop Started on port 8000")
    yield
    if heartbeat_task:
        heartbeat_task.cancel()

app = FastAPI(
    title=config.app_name,
    version=config.version,
    lifespan=lifespan
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def get_index():
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path)

@app.get("/api/config")
async def get_app_config():
    return {
        "app_name": config.app_name,
        "version": config.version,
        "active_provider": director.provider.provider_name,
        "cameras": [c.model_dump() for c in config.cameras],
        "policy": config.policy.model_dump()
    }

@app.get("/api/telemetry")
async def get_telemetry():
    telemetry = await director.step()
    return telemetry.model_dump()

class ManualCutRequest(BaseModel):
    camera_id: str
    lock_duration_sec: float = 6.0

@app.post("/api/cut")
async def manual_camera_cut(req: ManualCutRequest):
    valid_ids = [c.id for c in config.cameras]
    if req.camera_id not in valid_ids:
        raise HTTPException(status_code=400, detail=f"Invalid camera ID: {req.camera_id}")
    decision = director.manual_cut(req.camera_id, req.lock_duration_sec)
    return decision.model_dump()

class ToggleAutoRequest(BaseModel):
    enabled: bool

@app.post("/api/toggle-auto")
async def toggle_autonomous_mode(req: ToggleAutoRequest):
    director.is_auto_directing = req.enabled
    return {"status": "ok", "is_auto_directing": director.is_auto_directing}

class CameraStatusRequest(BaseModel):
    camera_id: str
    is_connected: bool

@app.post("/api/cameras/status")
async def set_camera_online_status(req: CameraStatusRequest):
    cams = director.set_camera_status(req.camera_id, req.is_connected)
    return {
        "status": "ok",
        "camera_id": req.camera_id,
        "is_connected": req.is_connected,
        "connected_cameras": cams,
        "active_camera_id": director.active_camera
    }

class ProviderSwitchRequest(BaseModel):
    provider: str

@app.post("/api/provider/switch")
async def switch_cloud_provider(req: ProviderSwitchRequest):
    from core.providers import get_active_provider
    new_provider = get_active_provider(req.provider)
    director.provider = new_provider
    return {
        "status": "ok",
        "provider_name": new_provider.provider_name
    }

@app.get("/api/benchmark")
async def run_benchmark():
    import time
    t0 = time.perf_counter()
    sam_res = await director.provider.segment_frame("cam_host")
    t1 = time.perf_counter()
    transcript_res = await director.provider.transcribe_audio_chunk()
    t2 = time.perf_counter()
    
    return {
        "status": "PASS",
        "provider": director.provider.provider_name,
        "sam_3_1_latency_ms": round((t1 - t0) * 1000, 2),
        "muse_voice_latency_ms": round((t2 - t1) * 1000, 2),
        "sam_detected_masks": len(sam_res.masks),
        "detected_emotions": transcript_res.detected_emotions
    }

class PointPromptRequest(BaseModel):
    camera_id: str
    point_x: float
    point_y: float

@app.post("/api/sam/point-prompt")
async def segment_point_prompt(req: PointPromptRequest):
    mask = await director.provider.segment_point(req.camera_id, req.point_x, req.point_y)
    if director.latest_sam:
        director.latest_sam.masks.insert(0, mask)
    return mask.model_dump()

@app.get("/api/export/edl")
async def export_edl_file():
    """Generates standard CMX 3600 Edit Decision List for DaVinci Resolve & Premiere Pro."""
    lines = [
        "TITLE: OMNIDIRECTOR_LIVE_BROADCAST",
        "FCM: NON-DROP FRAME",
        ""
    ]
    cur_sec = 0.0
    cuts = director.recent_cuts if director.recent_cuts else [
        {"camera": "CAM 1 — Host Prime", "type": "Cut", "reason": "Host opening cadence"},
        {"camera": "CAM 2 — Studio Wide", "type": "Dissolve", "reason": "Audience perspective refresh"},
        {"camera": "CAM 4 — Reaction Cam", "type": "Cut", "reason": "Guest punchline laughter"}
    ]
    
    for idx, c in enumerate(cuts, start=1):
        dur = 4.5
        in_tc = f"01:{int(cur_sec // 60):02d}:{int(cur_sec % 60):02d}:00"
        out_tc = f"01:{int((cur_sec + dur) // 60):02d}:{int((cur_sec + dur) % 60):02d}:00"
        src_tc = f"00:00:00:00 00:00:{int(dur):02d}:00"
        cam_code = "CAM1" if "Host" in c.get("camera", "") else "CAM2" if "Wide" in c.get("camera", "") else "CAM3" if "Screen" in c.get("camera", "") else "CAM4"
        trans = "D  030" if c.get("type") == "smooth_dissolve" else "C"
        
        lines.append(f"{idx:03d}  {cam_code}  V  {trans}        {src_tc} {in_tc} {out_tc}")
        lines.append(f"* FROM CLIP NAME: {cam_code}_1080P60.MOV")
        lines.append(f"* DIRECTORIAL REASON: {c.get('reason', 'Cadence synchronization')}")
        lines.append("")
        cur_sec += dur

    edl_content = "\n".join(lines)
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=edl_content,
        headers={"Content-Disposition": "attachment; filename=omnidirector_cutlist.edl"}
    )

@app.get("/api/meta-prompts")
async def get_meta_prompts():
    """Provides full transparency into Meta foundation model prompts and schemas."""
    return {
        "muse_spark": {
            "model": "meta-models/muse-spark-open-1026",
            "system_instruction": "You are the Executive Director of an autonomous 4-camera live studio. Arbitrate camera cuts with sub-second latency based on speaker cadence, emotional intensity, screen motion, and narrative pacing. Ensure dynamic 9:16 vertical crop coordinates track active subjects.",
            "output_schema": {
                "selected_camera_id": "string (enum: cam_host, cam_wide, cam_screen, cam_reaction)",
                "transition_type": "string (enum: hard_cut, smooth_dissolve, split_screen)",
                "kinetic_crop_x": "float (0.0 to 1.0)",
                "confidence": "float (0.0 to 1.0)",
                "is_climax_highlight": "boolean",
                "directorial_reasoning": "string"
            }
        },
        "sam_3_1": {
            "model": "Meta-SAM-3.1",
            "capabilities": ["zero_shot_spatio_temporal_segmentation", "point_prompting", "box_prompting"],
            "features": "Real-time subject mask extraction without green screens; sub-pixel boundary polygons for dynamic 9:16 pan-and-scan centering."
        },
        "muse_voice_transcribe": {
            "model": "Meta-Muse-Voice-Transcribe",
            "capabilities": ["word_level_timestamps", "energy_detection", "emotion_inflection", "silence_detection"]
        }
    }

# WebSocket for sub-second studio telemetry
@app.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send latest state to client
            telemetry = StreamTelemetry(
                active_camera_id=director.active_camera,
                active_camera_label=director.get_camera_label(director.active_camera),
                time_on_camera_sec=round(asyncio.get_event_loop().time() - director.last_cut_timestamp, 1),
                total_cuts_made=director.total_cuts,
                is_auto_directing=director.is_auto_directing,
                active_provider_name=director.provider.provider_name,
                latest_decision=director.latest_decision,
                latest_transcription=director.recent_transcripts[-1] if director.recent_transcripts else None,
                latest_sam_segmentation=director.latest_sam,
                kinetic_crop_x=round(director.kinetic_x, 3),
                kinetic_crop_y=round(director.kinetic_y, 3),
                climax_highlights_count=len(director.highlights),
                recent_cuts_history=director.recent_cuts[:6],
                connected_cameras=list(director.connected_cameras)
            )
            await websocket.send_text(telemetry.model_dump_json())
            await asyncio.sleep(0.8)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=config.port, reload=True)
