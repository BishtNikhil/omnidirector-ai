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
                recent_cuts_history=director.recent_cuts[:6]
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
