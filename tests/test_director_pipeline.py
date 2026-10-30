"""
OmniDirector AI — Comprehensive Pipeline & Contract Test Suite
"""
import pytest
import asyncio
from core.config import config
from core.providers.simulation_provider import SimulationOmniProvider
from core.agents.director_agent import DirectorAgent
from fastapi.testclient import TestClient
from app import app

def test_simulation_provider_contracts():
    async def _run():
        provider = SimulationOmniProvider()
        
        # 1. SAM 3.1 Frame Segmentation
        sam_res = await provider.segment_frame("cam_host")
        assert sam_res.model_version.startswith("Meta-SAM-3.1")
        assert len(sam_res.masks) >= 1
        assert sam_res.latency_ms > 0
        assert 0.0 <= sam_res.masks[0].confidence <= 1.0
        assert len(sam_res.masks[0].polygon_points) >= 3

        # 2. Muse Voice Transcribe
        transcript = await provider.transcribe_audio_chunk()
        assert transcript.model_version.startswith("Meta-Muse-Voice-Transcribe")
        assert len(transcript.text) > 0
        assert len(transcript.words) > 0
        assert 0.0 <= transcript.energy_score <= 1.0

        # 3. Muse Spark Directorial Arbitration
        decision = await provider.evaluate_directorial_cut(
            current_camera="cam_host",
            recent_transcripts=[transcript],
            visual_activity={"cam_host": 0.6, "cam_screen": 0.8},
            duration_on_current_cam_sec=4.0
        )
        assert decision.model_version.startswith("Meta-Muse-Spark")
        assert decision.selected_camera_id in [c.id for c in config.cameras]
        assert len(decision.reasoning) > 0
        
    asyncio.run(_run())

def test_director_agent_lifecycle():
    async def _run():
        director = DirectorAgent(provider=SimulationOmniProvider())
        
        # Initial state
        assert director.active_camera == "cam_host"
        assert director.total_cuts == 0
        
        # Run 3 heartbeat steps
        for _ in range(3):
            telemetry = await director.step()
            assert telemetry.active_camera_id in [c.id for c in config.cameras]
            assert telemetry.time_on_camera_sec >= 0.0
            assert 0.0 <= telemetry.kinetic_crop_x <= 1.0

        # Test manual creator cut override
        decision = director.manual_cut("cam_screen", lock_duration_sec=5.0)
        assert director.active_camera == "cam_screen"
        assert director.total_cuts >= 1
        assert decision.selected_camera_id == "cam_screen"

    asyncio.run(_run())

def test_fastapi_endpoints():
    client = TestClient(app)
    
    # 1. Config endpoint
    res_cfg = client.get("/api/config")
    assert res_cfg.status_code == 200
    data_cfg = res_cfg.json()
    assert len(data_cfg["cameras"]) == 4
    
    # 2. Telemetry endpoint
    res_tel = client.get("/api/telemetry")
    assert res_tel.status_code == 200
    data_tel = res_tel.json()
    assert "active_camera_id" in data_tel
    assert "kinetic_crop_x" in data_tel
    
    # 3. Manual cut API
    res_cut = client.post("/api/cut", json={"camera_id": "cam_reaction", "lock_duration_sec": 4.0})
    assert res_cut.status_code == 200
    assert res_cut.json()["selected_camera_id"] == "cam_reaction"
    
    # 4. Benchmark API
    res_bm = client.get("/api/benchmark")
    assert res_bm.status_code == 200
    data_bm = res_bm.json()
    assert data_bm["status"] == "PASS"
    assert data_bm["sam_3_1_latency_ms"] >= 0

    # 5. SAM 3.1 Point Prompt API
    res_pt = client.post("/api/sam/point-prompt", json={"camera_id": "cam_host", "point_x": 0.5, "point_y": 0.4})
    assert res_pt.status_code == 200
    data_pt = res_pt.json()
    assert "label" in data_pt
    assert len(data_pt["polygon_points"]) >= 3

    # 6. EDL Export API
    res_edl = client.get("/api/export/edl")
    assert res_edl.status_code == 200
    assert "TITLE: OMNIDIRECTOR_LIVE_BROADCAST" in res_edl.text
    assert "FCM: NON-DROP FRAME" in res_edl.text

    # 7. Meta Model Prompts Transparency API
    res_meta = client.get("/api/meta-prompts")
    assert res_meta.status_code == 200
    data_meta = res_meta.json()
    assert "muse_spark" in data_meta
    assert "sam_3_1" in data_meta
    assert "muse_voice_transcribe" in data_meta

    # 8. Camera Online/Offline Status Toggle API
    res_cam_off = client.post("/api/cameras/status", json={"camera_id": "cam_reaction", "is_connected": False})
    assert res_cam_off.status_code == 200
    assert "cam_reaction" not in res_cam_off.json()["connected_cameras"]
    
    # Restore cam_reaction
    res_cam_on = client.post("/api/cameras/status", json={"camera_id": "cam_reaction", "is_connected": True})
    assert res_cam_on.status_code == 200
    assert "cam_reaction" in res_cam_on.json()["connected_cameras"]

    # 9. Provider Switch API
    res_sw_baseten = client.post("/api/provider/switch", json={"provider": "baseten"})
    assert res_sw_baseten.status_code == 200
    assert "baseten" in res_sw_baseten.json()["provider_name"].lower()

    res_sw_meta = client.post("/api/provider/switch", json={"provider": "meta"})
    assert res_sw_meta.status_code == 200
    assert "meta" in res_sw_meta.json()["provider_name"].lower()

    res_sw_sim = client.post("/api/provider/switch", json={"provider": "simulation"})
    assert res_sw_sim.status_code == 200
    assert "simulation" in res_sw_sim.json()["provider_name"].lower()

