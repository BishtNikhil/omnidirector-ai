/**
 * OmniDirector AI — Interactive Studio Client Controller
 * Manages WebSocket telemetry, real-time SAM 3.1 polygon rendering,
 * multicam matrix switching, and kinetic 9:16 vertical pan-and-scan.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const activeProviderLabel = document.getElementById('activeProviderLabel');
    const activeCamTitle = document.getElementById('activeCamTitle');
    const shotClockTimer = document.getElementById('shotClockTimer');
    const toggleSamMasks = document.getElementById('toggleSamMasks');
    const samCanvas = document.getElementById('samOverlayCanvas');
    const samCtx = samCanvas.getContext('2d');
    
    const virtualFeedScene = document.getElementById('virtualFeedScene');
    const feedBgLayer = document.getElementById('feedBgLayer');
    const feedSubjectLayer = document.getElementById('feedSubjectLayer');
    
    const subtitleSpeaker = document.getElementById('subtitleSpeaker');
    const subtitleText = document.getElementById('subtitleText');
    const climaxFlash = document.getElementById('climaxFlashEffect');
    
    const statTotalCuts = document.getElementById('statTotalCuts');
    const statHighlights = document.getElementById('statHighlights');
    const statKineticCrop = document.getElementById('statKineticCrop');
    
    const btnToggleAuto = document.getElementById('btnToggleAuto');
    const txtAutoStatus = document.getElementById('txtAutoStatus');
    const camCardsGrid = document.getElementById('camCardsGrid');
    
    // Sidebar elements
    const verticalSubjectSim = document.getElementById('verticalSubjectSim');
    const verticalCaptions = document.getElementById('verticalCaptions');
    const reasoningBubble = document.getElementById('reasoningBubble');
    const reasoningModelTag = document.getElementById('reasoningModelTag');
    const reasoningConfidence = document.getElementById('reasoningConfidence');
    const samLatencyTag = document.getElementById('samLatencyTag');
    const samMasksList = document.getElementById('samMasksList');
    const detectedEmotionsTag = document.getElementById('detectedEmotionsTag');
    const audioEnergyFill = document.getElementById('audioEnergyFill');
    const audioEnergyVal = document.getElementById('audioEnergyVal');
    const waveformCanvas = document.getElementById('audioWaveformCanvas');
    const waveformCtx = waveformCanvas.getContext('2d');
    const cutsHistoryList = document.getElementById('cutsHistoryList');

    // State
    let cameras = [];
    let activeCameraId = "cam_host";
    let isAutoDirecting = true;
    let showSamMasks = true;
    let shotStartTime = Date.now();
    let currentMasks = [];
    let kineticX = 0.5;
    let wavePhase = 0;

    // Set canvas dimensions
    function resizeCanvas() {
        const rect = samCanvas.getBoundingClientRect();
        samCanvas.width = rect.width * window.devicePixelRatio;
        samCanvas.height = rect.height * window.devicePixelRatio;
        samCtx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }
    window.addEventListener('resize', resizeCanvas);
    setTimeout(resizeCanvas, 100);

    // Fetch initial configuration
    async function loadConfig() {
        try {
            const res = await fetch('/api/config');
            const data = await res.json();
            activeProviderLabel.textContent = data.active_provider;
            cameras = data.cameras;
            renderCameraCards();
        } catch (e) {
            console.error("Config fetch error:", e);
        }
    }

    // Render 4-Camera Multiview Cards
    function renderCameraCards() {
        camCardsGrid.innerHTML = '';
        cameras.forEach(cam => {
            const card = document.createElement('div');
            card.className = `cam-preview-card ${cam.id === activeCameraId ? 'is-active-cam' : ''}`;
            card.id = `card_${cam.id}`;
            card.innerHTML = `
                <div class="cam-thumb-box">
                    <span class="cam-live-indicator">${cam.id === activeCameraId ? 'PROGRAM' : 'PREVIEW'}</span>
                    <div style="font-size: 28px; opacity: 0.7;">
                        ${cam.role === 'host' ? '🎙️' : cam.role === 'wide' ? '🏛️' : cam.role === 'screen' ? '💻' : '⚡'}
                    </div>
                </div>
                <div class="cam-card-meta">
                    <span class="cam-card-name">${cam.label}</span>
                    <span class="cam-card-role">${cam.role}</span>
                </div>
            `;
            card.addEventListener('click', () => triggerManualCut(cam.id));
            camCardsGrid.appendChild(card);
        });
    }

    // Manual camera cut handler
    async function triggerManualCut(cameraId) {
        try {
            const res = await fetch('/api/cut', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ camera_id: cameraId, lock_duration_sec: 6.0 })
            });
            const data = await res.json();
            activeCameraId = cameraId;
            shotStartTime = Date.now();
            updateActiveCameraUI();
        } catch (e) {
            console.error("Manual cut error:", e);
        }
    }

    // Toggle Autonomous Directing
    btnToggleAuto.addEventListener('click', async () => {
        isAutoDirecting = !isAutoDirecting;
        try {
            await fetch('/api/toggle-auto', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: isAutoDirecting })
            });
            btnToggleAuto.className = `btn-director-toggle ${isAutoDirecting ? 'active' : 'paused'}`;
            txtAutoStatus.textContent = isAutoDirecting ? 'AUTONOMOUS' : 'MANUAL HOLD';
        } catch (e) {
            console.error("Toggle error:", e);
        }
    });

    toggleSamMasks.addEventListener('change', (e) => {
        showSamMasks = e.target.checked;
        if (!showSamMasks) {
            const rect = samCanvas.getBoundingClientRect();
            samCtx.clearRect(0, 0, rect.width, rect.height);
        }
    });

    function updateActiveCameraUI() {
        const cam = cameras.find(c => c.id === activeCameraId);
        if (cam) {
            activeCamTitle.textContent = cam.label;
        }
        document.querySelectorAll('.cam-preview-card').forEach(c => {
            const isCur = c.id === `card_${activeCameraId}`;
            c.classList.toggle('is-active-cam', isCur);
            c.querySelector('.cam-live-indicator').textContent = isCur ? 'PROGRAM' : 'PREVIEW';
        });

        // Thematic background shift per camera role
        if (activeCameraId === 'cam_screen') {
            feedBgLayer.style.background = 'radial-gradient(circle, #0F2027 0%, #203A43 50%, #2C5364 100%)';
            feedSubjectLayer.style.left = '25%';
        } else if (activeCameraId === 'cam_reaction') {
            feedBgLayer.style.background = 'radial-gradient(circle, #200122 0%, #6f0000 100%)';
            feedSubjectLayer.style.left = '75%';
        } else if (activeCameraId === 'cam_wide') {
            feedBgLayer.style.background = 'radial-gradient(circle, #141E30 0%, #243B55 100%)';
            feedSubjectLayer.style.left = '50%';
        } else {
            feedBgLayer.style.background = 'linear-gradient(135deg, #091220 0%, #03060B 100%)';
            feedSubjectLayer.style.left = '50%';
        }
    }

    // Shot Clock animation
    setInterval(() => {
        const elapsed = (Date.now() - shotStartTime) / 1000;
        const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
        const secs = (elapsed % 60).toFixed(1).padStart(4, '0');
        shotClockTimer.textContent = `${mins}:${secs}`;
    }, 100);

    // Draw SAM 3.1 Polygonal Masks on 16:9 Canvas
    function drawSAMMasks() {
        if (!showSamMasks || !currentMasks || currentMasks.length === 0) return;
        const rect = samCanvas.getBoundingClientRect();
        const W = rect.width;
        const H = rect.height;

        samCtx.clearRect(0, 0, W, H);

        const colors = [
            { stroke: '#00F2FE', fill: 'rgba(0, 242, 254, 0.18)' },
            { stroke: '#38EF7D', fill: 'rgba(56, 239, 125, 0.18)' },
            { stroke: '#FFB300', fill: 'rgba(255, 179, 0, 0.18)' }
        ];

        currentMasks.forEach((m, idx) => {
            if (!m.polygon_points || m.polygon_points.length === 0) return;
            const style = colors[idx % colors.length];

            samCtx.beginPath();
            const first = m.polygon_points[0];
            samCtx.moveTo(first[0] * W, first[1] * H);

            for (let i = 1; i < m.polygon_points.length; i++) {
                const pt = m.polygon_points[i];
                samCtx.lineTo(pt[0] * W, pt[1] * H);
            }
            samCtx.closePath();

            samCtx.fillStyle = style.fill;
            samCtx.fill();
            samCtx.strokeStyle = style.stroke;
            samCtx.lineWidth = 2;
            samCtx.stroke();

            // Mask Label Badge
            const labelX = m.polygon_points[0][0] * W;
            const labelY = Math.max(20, m.polygon_points[0][1] * H - 8);

            samCtx.font = '600 11px Outfit, sans-serif';
            const textWidth = samCtx.measureText(m.label).width;

            samCtx.fillStyle = 'rgba(8, 11, 16, 0.85)';
            samCtx.fillRect(labelX - 4, labelY - 14, textWidth + 8, 18);
            samCtx.strokeStyle = style.stroke;
            samCtx.lineWidth = 1;
            samCtx.strokeRect(labelX - 4, labelY - 14, textWidth + 8, 18);

            samCtx.fillStyle = style.stroke;
            samCtx.fillText(m.label, labelX, labelY);
        });
    }

    // Draw Audio Waveform
    function drawWaveform() {
        const W = waveformCanvas.width;
        const H = waveformCanvas.height;
        waveformCtx.clearRect(0, 0, W, H);

        waveformCtx.beginPath();
        waveformCtx.moveTo(0, H / 2);
        wavePhase += 0.08;

        for (let x = 0; x < W; x++) {
            const y = (H / 2) + Math.sin(x * 0.05 + wavePhase) * 10 * Math.sin(x * 0.02);
            waveformCtx.lineTo(x, y);
        }
        waveformCtx.strokeStyle = '#00F2FE';
        waveformCtx.lineWidth = 2;
        waveformCtx.stroke();
    }
    setInterval(drawWaveform, 40);

    // WebSocket Telemetry Connection
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/telemetry`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("⚡ OmniDirector WebSocket Telemetry Connected");
        };

        ws.onmessage = (event) => {
            const telemetry = JSON.parse(event.data);
            handleTelemetryUpdate(telemetry);
        };

        ws.onclose = () => {
            console.log("WebSocket disconnected. Reconnecting in 2s...");
            setTimeout(connectWebSocket, 2000);
        };
    }

    // Handle Incoming Telemetry Heartbeat
    function handleTelemetryUpdate(t) {
        if (t.active_camera_id !== activeCameraId) {
            activeCameraId = t.active_camera_id;
            shotStartTime = Date.now();
            updateActiveCameraUI();
        }

        activeProviderLabel.textContent = t.active_provider_name;
        statTotalCuts.textContent = t.total_cuts_made;
        statHighlights.textContent = t.climax_highlights_count;
        statKineticCrop.textContent = `X: ${t.kinetic_crop_x.toFixed(2)}`;

        // Transcription & Lower-Third
        if (t.latest_transcription) {
            subtitleSpeaker.textContent = t.latest_transcription.speaker_id.toUpperCase();
            subtitleText.textContent = t.latest_transcription.text;
            detectedEmotionsTag.textContent = t.latest_transcription.detected_emotions.join(', ') || 'Engaged';
            
            const energyPct = Math.round(t.latest_transcription.energy_score * 100);
            audioEnergyFill.style.width = `${energyPct}%`;
            audioEnergyVal.textContent = `${energyPct}%`;

            // Animate Vertical Karaoke Captions
            if (t.latest_transcription.words && t.latest_transcription.words.length > 0) {
                const words = t.latest_transcription.words.slice(0, 6);
                verticalCaptions.innerHTML = words.map((w, idx) => 
                    `<span class="karaoke-word ${idx === words.length - 1 ? 'highlight' : ''}">${w.word}</span>`
                ).join(' ');
            }
        }

        // SAM 3.1 Masks
        if (t.latest_sam_segmentation) {
            samLatencyTag.textContent = `Latency: ${t.latest_sam_segmentation.latency_ms}ms`;
            currentMasks = t.latest_sam_segmentation.masks || [];
            drawSAMMasks();

            // Populate Masks Inspector List
            samMasksList.innerHTML = currentMasks.map(m => `
                <div class="mask-item-row">
                    <div class="mask-item-name">
                        <span class="mask-color-dot" style="background: #00F2FE;"></span>
                        <span>${m.label}</span>
                    </div>
                    <span class="mask-conf-val">${(m.confidence * 100).toFixed(1)}%</span>
                </div>
            `).join('');
        }

        // Kinetic Pan & Scan
        if (t.kinetic_crop_x !== undefined) {
            kineticX = t.kinetic_crop_x;
            const shiftPct = (kineticX - 0.5) * 40;
            verticalSubjectSim.style.transform = `translateX(calc(-50% + ${shiftPct}px))`;
        }

        // Muse Spark Reasoning
        if (t.latest_decision) {
            reasoningBubble.textContent = t.latest_decision.reasoning;
            reasoningModelTag.textContent = t.latest_decision.model_version;
            reasoningConfidence.textContent = `Confidence: ${(t.latest_decision.confidence * 100).toFixed(0)}%`;

            if (t.latest_decision.is_climax_highlight) {
                climaxFlash.classList.add('flash-active');
                setTimeout(() => climaxFlash.classList.remove('flash-active'), 600);
            }
        }

        // Cuts History
        if (t.recent_cuts_history) {
            cutsHistoryList.innerHTML = t.recent_cuts_history.map(c => `
                <li class="cut-history-item">
                    <div class="cut-item-header">
                        <span class="cut-item-cam">${c.camera}</span>
                        <span class="cut-item-time">${c.timestamp} • ${c.type}</span>
                    </div>
                    <p class="cut-item-reason">${c.reason}</p>
                </li>
            `).join('');
        }
    }

    // Start
    loadConfig();
    connectWebSocket();
});
