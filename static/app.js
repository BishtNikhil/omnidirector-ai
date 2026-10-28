/**
 * OmniDirector Studio — Professional Minimalist Controller
 * Manages dual-theme switching (Light Washout / Dark), real-time studio canvas rendering,
 * SAM 3.1 polygonal segmentation tracking, multi-camera matrix switching,
 * and kinetic 9:16 vertical pan-and-scan.
 */

document.addEventListener('DOMContentLoaded', () => {
    // --------------------------------------------------------------------------
    // Theme Management (Light Washout Default)
    // --------------------------------------------------------------------------
    const btnThemeToggle = document.getElementById('btnThemeToggle');
    const themeIcon = document.getElementById('themeIcon');
    let currentTheme = localStorage.getItem('omnidirector_theme') || 'light';

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        currentTheme = theme;
        localStorage.setItem('omnidirector_theme', theme);
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
    applyTheme(currentTheme);

    btnThemeToggle.addEventListener('click', () => {
        applyTheme(currentTheme === 'light' ? 'dark' : 'light');
    });

    // --------------------------------------------------------------------------
    // DOM Element Bindings
    // --------------------------------------------------------------------------
    const activeProviderLabel = document.getElementById('activeProviderLabel');
    const activeCamTitle = document.getElementById('activeCamTitle');
    const shotClockTimer = document.getElementById('shotClockTimer');
    const toggleSafeGuides = document.getElementById('toggleSafeGuides');
    const safeGuidesOverlay = document.getElementById('safeGuidesOverlay');
    const toggleSamMasks = document.getElementById('toggleSamMasks');

    const studioCanvas = document.getElementById('studioMainCanvas');
    const studioCtx = studioCanvas.getContext('2d');
    const reelCanvas = document.getElementById('reelCanvas');
    const reelCtx = reelCanvas.getContext('2d');

    const subtitleSpeaker = document.getElementById('subtitleSpeaker');
    const subtitleText = document.getElementById('subtitleText');
    const climaxTint = document.getElementById('climaxTint');

    const statTotalCuts = document.getElementById('statTotalCuts');
    const statHighlights = document.getElementById('statHighlights');
    const statKineticCrop = document.getElementById('statKineticCrop');
    const btnToggleAuto = document.getElementById('btnToggleAuto');
    const txtAutoStatus = document.getElementById('txtAutoStatus');

    const camerasGrid = document.getElementById('camerasGrid');
    const timelineProgressBar = document.getElementById('timelineProgressBar');
    const timelineMarkersLayer = document.getElementById('timelineMarkersLayer');
    const timelineBeatLabel = document.getElementById('timelineBeatLabel');

    const reelCaptions = document.getElementById('reelCaptions');
    const reasoningBubble = document.getElementById('reasoningBubble');
    const reasoningModelTag = document.getElementById('reasoningModelTag');
    const reasoningConfidence = document.getElementById('reasoningConfidence');
    const samLatencyTag = document.getElementById('samLatencyTag');
    const samMasksList = document.getElementById('samMasksList');
    const detectedEmotionsTag = document.getElementById('detectedEmotionsTag');
    const vuFill = document.getElementById('vuFill');
    const waveformCanvas = document.getElementById('waveformCanvas');
    const waveformCtx = waveformCanvas.getContext('2d');
    const cutsFeed = document.getElementById('cutsFeed');

    // Preset Buttons
    document.querySelectorAll('.tool-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tool-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const preset = tab.dataset.preset;
            if (preset === 'keynote') {
                triggerManualCut('cam_screen');
            } else if (preset === 'podcast') {
                triggerManualCut('cam_host');
            } else if (preset === 'creator') {
                triggerManualCut('cam_reaction');
            }
        });
    });

    // --------------------------------------------------------------------------
    // State Architecture
    // --------------------------------------------------------------------------
    let cameras = [];
    let activeCameraId = "cam_host";
    let isAutoDirecting = true;
    let showSamMasks = true;
    let shotStartTime = Date.now();
    let currentMasks = [];
    let kineticX = 0.5;
    let kineticY = 0.5;
    let wavePhase = 0;
    let animFrame = 0;
    let sessionStartMs = Date.now();

    // Canvas Resizing
    function resizeCanvases() {
        const sRect = studioCanvas.getBoundingClientRect();
        studioCanvas.width = sRect.width * window.devicePixelRatio;
        studioCanvas.height = sRect.height * window.devicePixelRatio;

        const rRect = reelCanvas.getBoundingClientRect();
        reelCanvas.width = rRect.width * window.devicePixelRatio;
        reelCanvas.height = rRect.height * window.devicePixelRatio;
    }
    window.addEventListener('resize', resizeCanvases);
    setTimeout(resizeCanvases, 150);

    toggleSafeGuides.addEventListener('change', (e) => {
        safeGuidesOverlay.style.display = e.target.checked ? 'block' : 'none';
    });

    toggleSamMasks.addEventListener('change', (e) => {
        showSamMasks = e.target.checked;
    });

    // --------------------------------------------------------------------------
    // Broadcast Canvas Rendering Engine (Cinematic Studio Visuals)
    // --------------------------------------------------------------------------
    function renderStudioScene() {
        animFrame++;
        const W = studioCanvas.width;
        const H = studioCanvas.height;
        if (!W || !H) return;

        studioCtx.clearRect(0, 0, W, H);
        const t = (Date.now() - sessionStartMs) / 1000;

        // Draw Scene based on Active Camera
        if (activeCameraId === 'cam_host') {
            drawHostPrimeScene(studioCtx, W, H, t);
        } else if (activeCameraId === 'cam_wide') {
            drawWideStudioScene(studioCtx, W, H, t);
        } else if (activeCameraId === 'cam_screen') {
            drawScreenHudScene(studioCtx, W, H, t);
        } else {
            drawReactionScene(studioCtx, W, H, t);
        }

        // Draw SAM 3.1 Segmentation Contours if toggled
        if (showSamMasks && currentMasks && currentMasks.length > 0) {
            drawSAMPolygons(studioCtx, W, H);
        }

        // Render 9:16 Vertical Reel Crop
        renderVerticalReel(t);
    }

    function drawHostPrimeScene(ctx, W, H, t) {
        // Deep Warm Studio Lighting Gradient
        const grad = ctx.createLinearGradient(0, 0, W, H);
        grad.addColorStop(0, '#1E2430');
        grad.addColorStop(0.5, '#141822');
        grad.addColorStop(1, '#0C0F15');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, W, H);

        // Acoustic Panel Slats on Background Wall
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
        ctx.lineWidth = 14 * (W / 1200);
        for (let x = W * 0.1; x < W * 0.9; x += W * 0.06) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, H * 0.7);
            ctx.stroke();
        }

        // Warm Ambient Backlight (Slight Amber Halo)
        const halo = ctx.createRadialGradient(W * 0.5, H * 0.42, 10, W * 0.5, H * 0.42, W * 0.35);
        halo.addColorStop(0, 'rgba(212, 150, 80, 0.18)');
        halo.addColorStop(0.7, 'rgba(72, 97, 134, 0.12)');
        halo.addColorStop(1, 'transparent');
        ctx.fillStyle = halo;
        ctx.fillRect(0, 0, W, H);

        // Host Subject Silhouette with Studio Lighting Highlights
        const breath = Math.sin(t * 1.8) * 3;
        const headX = W * 0.5;
        const headY = H * 0.42 + breath;
        const headR = H * 0.14;

        // Shoulders / Torso
        ctx.fillStyle = '#181E29';
        ctx.beginPath();
        ctx.moveTo(headX - headR * 2.2, H);
        ctx.lineTo(headX - headR * 1.6, headY + headR * 1.4);
        ctx.quadraticCurveTo(headX, headY + headR * 1.1, headX + headR * 1.6, headY + headR * 1.4);
        ctx.lineTo(headX + headR * 2.2, H);
        ctx.closePath();
        ctx.fill();

        // Rim Lighting on Shoulders
        ctx.strokeStyle = 'rgba(200, 214, 232, 0.3)';
        ctx.lineWidth = 3;
        ctx.stroke();

        // Head
        ctx.fillStyle = '#283142';
        ctx.beginPath();
        ctx.arc(headX, headY, headR, 0, Math.PI * 2);
        ctx.fill();

        // Head Rim Light
        ctx.strokeStyle = 'rgba(234, 219, 202, 0.45)';
        ctx.lineWidth = 2.5;
        ctx.stroke();

        // Shure SM7B Style Studio Microphone on Boom Arm
        const micX = W * 0.38;
        const micY = H * 0.62;
        ctx.fillStyle = '#0F131A';
        ctx.beginPath();
        ctx.roundRect(micX - 16, micY - 32, 32, 64, 8);
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Boom Arm line
        ctx.strokeStyle = '#181C24';
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(micX - 16, micY);
        ctx.lineTo(W * 0.18, H * 0.88);
        ctx.stroke();
    }

    function drawWideStudioScene(ctx, W, H, t) {
        // Wide Studio Master View
        const grad = ctx.createLinearGradient(0, 0, W, H);
        grad.addColorStop(0, '#161C26');
        grad.addColorStop(1, '#0C0F14');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, W, H);

        // Studio Table Podium
        ctx.fillStyle = '#1A212E';
        ctx.beginPath();
        ctx.moveTo(W * 0.12, H * 0.95);
        ctx.lineTo(W * 0.25, H * 0.65);
        ctx.lineTo(W * 0.75, H * 0.65);
        ctx.lineTo(W * 0.88, H * 0.95);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        ctx.stroke();

        // Host on Left
        ctx.fillStyle = '#263042';
        ctx.beginPath();
        ctx.arc(W * 0.35, H * 0.46, H * 0.08, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillRect(W * 0.30, H * 0.54, W * 0.10, H * 0.14);

        // Guest on Right
        ctx.fillStyle = '#2C374C';
        ctx.beginPath();
        ctx.arc(W * 0.65, H * 0.46, H * 0.08, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillRect(W * 0.60, H * 0.54, W * 0.10, H * 0.14);

        // Center Studio Screen Graphic
        ctx.fillStyle = 'rgba(72, 97, 134, 0.15)';
        ctx.strokeStyle = 'rgba(72, 97, 134, 0.4)';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(W * 0.42, H * 0.28, W * 0.16, H * 0.18);
        ctx.fillRect(W * 0.42, H * 0.28, W * 0.16, H * 0.18);
    }

    function drawScreenHudScene(ctx, W, H, t) {
        // High-Tech IDE / Telemetry Screen
        ctx.fillStyle = '#0F1217';
        ctx.fillRect(0, 0, W, H);

        // Left Code Editor Window
        ctx.fillStyle = '#151922';
        ctx.fillRect(W * 0.04, H * 0.08, W * 0.52, H * 0.84);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        ctx.strokeRect(W * 0.04, H * 0.08, W * 0.52, H * 0.84);

        // Mock Code Lines
        const codeColors = ['#4F7A67', '#486186', '#B08244', '#8591A5'];
        for (let y = H * 0.16; y < H * 0.82; y += H * 0.055) {
            ctx.fillStyle = codeColors[Math.floor(y * 10) % codeColors.length];
            const lineW = (Math.sin(y * 2) * 0.15 + 0.3) * W;
            ctx.fillRect(W * 0.08, y, lineW, 8 * (H / 600));
        }

        // Right Telemetry Dashboard
        ctx.fillStyle = '#1A212E';
        ctx.fillRect(W * 0.60, H * 0.08, W * 0.36, H * 0.84);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        ctx.strokeRect(W * 0.60, H * 0.08, W * 0.36, H * 0.84);

        // Live Sine Graph
        ctx.strokeStyle = '#4F7A67';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.moveTo(W * 0.64, H * 0.45);
        for (let x = W * 0.64; x < W * 0.92; x += 4) {
            const y = H * 0.45 + Math.sin(x * 0.03 + t * 4) * 22;
            ctx.lineTo(x, y);
        }
        ctx.stroke();
    }

    function drawReactionScene(ctx, W, H, t) {
        // Profile Reaction Shot
        const grad = ctx.createLinearGradient(0, 0, W, H);
        grad.addColorStop(0, '#211B24');
        grad.addColorStop(1, '#0F0D13');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, W, H);

        const breath = Math.sin(t * 2.2) * 4;
        const headX = W * 0.55;
        const headY = H * 0.44 + breath;

        // Guest Profile Head
        ctx.fillStyle = '#312738';
        ctx.beginPath();
        ctx.ellipse(headX, headY, H * 0.13, H * 0.16, -0.15, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = 'rgba(224, 109, 91, 0.4)';
        ctx.lineWidth = 2.5;
        ctx.stroke();

        // Torso
        ctx.fillStyle = '#1B1622';
        ctx.fillRect(W * 0.38, H * 0.60, W * 0.35, H * 0.40);
    }

    // --------------------------------------------------------------------------
    // SAM 3.1 Polygonal Segmentation Renderer (Washed-out Minimalist Style)
    // --------------------------------------------------------------------------
    function drawSAMPolygons(ctx, W, H) {
        const styles = [
            { stroke: '#4F7A67', fill: 'rgba(79, 122, 103, 0.14)', bg: '#EEF5F1' },
            { stroke: '#486186', fill: 'rgba(72, 97, 134, 0.14)', bg: '#EEF3F9' },
            { stroke: '#B08244', fill: 'rgba(176, 130, 68, 0.14)', bg: '#FAF4EC' }
        ];

        currentMasks.forEach((m, idx) => {
            if (!m.polygon_points || m.polygon_points.length === 0) return;
            const style = styles[idx % styles.length];

            ctx.beginPath();
            const first = m.polygon_points[0];
            ctx.moveTo(first[0] * W, first[1] * H);

            for (let i = 1; i < m.polygon_points.length; i++) {
                const pt = m.polygon_points[i];
                ctx.lineTo(pt[0] * W, pt[1] * H);
            }
            ctx.closePath();

            ctx.fillStyle = style.fill;
            ctx.fill();

            // Refined dashed hairline stroke
            ctx.strokeStyle = style.stroke;
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 4]);
            ctx.stroke();
            ctx.setLineDash([]);

            // Minimalist Label Tag
            const labelX = m.polygon_points[0][0] * W;
            const labelY = Math.max(24, m.polygon_points[0][1] * H - 8);

            ctx.font = '600 11px Outfit, sans-serif';
            const textWidth = ctx.measureText(m.label).width;

            ctx.fillStyle = '#FFFFFF';
            ctx.shadowColor = 'rgba(0,0,0,0.1)';
            ctx.shadowBlur = 4;
            ctx.fillRect(labelX - 4, labelY - 14, textWidth + 8, 18);
            ctx.shadowBlur = 0;

            ctx.strokeStyle = style.stroke;
            ctx.lineWidth = 1;
            ctx.strokeRect(labelX - 4, labelY - 14, textWidth + 8, 18);

            ctx.fillStyle = style.stroke;
            ctx.fillText(m.label, labelX, labelY);
        });
    }

    // --------------------------------------------------------------------------
    // 9:16 Kinetic Vertical Reel Renderer
    // --------------------------------------------------------------------------
    function renderVerticalReel(t) {
        const W = reelCanvas.width;
        const H = reelCanvas.height;
        if (!W || !H) return;

        reelCtx.clearRect(0, 0, W, H);

        // Copy cropped section from main studio canvas based on kineticX
        const sW = studioCanvas.width;
        const sH = studioCanvas.height;

        const cropW = sH * (9 / 16);
        const cropH = sH;
        let cropX = (kineticX * sW) - (cropW / 2);
        cropX = Math.max(0, Math.min(sW - cropW, cropX));

        reelCtx.drawImage(studioCanvas, cropX, 0, cropW, cropH, 0, 0, W, H);
    }

    // Loop
    setInterval(renderStudioScene, 35);

    // --------------------------------------------------------------------------
    // Waveform Oscillations
    // --------------------------------------------------------------------------
    function drawWaveform() {
        const W = waveformCanvas.width;
        const H = waveformCanvas.height;
        waveformCtx.clearRect(0, 0, W, H);

        waveformCtx.beginPath();
        waveformCtx.moveTo(0, H / 2);
        wavePhase += 0.06;

        for (let x = 0; x < W; x++) {
            const y = (H / 2) + Math.sin(x * 0.06 + wavePhase) * 8 * Math.sin(x * 0.02);
            waveformCtx.lineTo(x, y);
        }
        waveformCtx.strokeStyle = currentTheme === 'dark' ? '#6382B0' : '#486186';
        waveformCtx.lineWidth = 1.5;
        waveformCtx.stroke();
    }
    setInterval(drawWaveform, 40);

    // --------------------------------------------------------------------------
    // Fetch Configuration & Cameras
    // --------------------------------------------------------------------------
    async function loadConfig() {
        try {
            const res = await fetch('/api/config');
            const data = await res.json();
            activeProviderLabel.textContent = data.active_provider;
            cameras = data.cameras;
            renderCamerasGrid();
        } catch (e) {
            console.error("Config fetch error:", e);
        }
    }

    function renderCamerasGrid() {
        camerasGrid.innerHTML = '';
        cameras.forEach(cam => {
            const tile = document.createElement('div');
            tile.className = `cam-tile ${cam.id === activeCameraId ? 'on-air-active' : ''}`;
            tile.id = `tile_${cam.id}`;
            tile.innerHTML = `
                <div class="cam-viewport-thumb">
                    <span class="cam-tally-tag">${cam.id === activeCameraId ? 'PROGRAM' : 'PREVIEW'}</span>
                    <div style="font-size: 24px; opacity: 0.65;">
                        ${cam.role === 'host' ? '🎙️' : cam.role === 'wide' ? '🏛️' : cam.role === 'screen' ? '💻' : '⚡'}
                    </div>
                </div>
                <div class="cam-tile-footer">
                    <span class="cam-tile-name">${cam.label}</span>
                    <span class="cam-tile-role">${cam.role}</span>
                </div>
            `;
            tile.addEventListener('click', () => triggerManualCut(cam.id));
            camerasGrid.appendChild(tile);
        });
    }

    async function triggerManualCut(camId) {
        try {
            await fetch('/api/cut', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ camera_id: camId, lock_duration_sec: 6.0 })
            });
            activeCameraId = camId;
            shotStartTime = Date.now();
            updateCameraActiveState();
        } catch (e) {
            console.error("Manual cut error:", e);
        }
    }

    function updateCameraActiveState() {
        const cam = cameras.find(c => c.id === activeCameraId);
        if (cam) {
            activeCamTitle.textContent = cam.label;
        }
        document.querySelectorAll('.cam-tile').forEach(t => {
            const isCur = t.id === `tile_${activeCameraId}`;
            t.classList.toggle('on-air-active', isCur);
            t.querySelector('.cam-tally-tag').textContent = isCur ? 'PROGRAM' : 'PREVIEW';
        });
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
            btnToggleAuto.className = `btn-director-mode ${isAutoDirecting ? 'active' : ''}`;
            txtAutoStatus.textContent = isAutoDirecting ? 'AUTONOMOUS' : 'MANUAL HOLD';
        } catch (e) {
            console.error("Auto toggle error:", e);
        }
    });

    // Shot Clock Timer (HH:MM:SS.d)
    setInterval(() => {
        const elapsed = (Date.now() - shotStartTime) / 1000;
        const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
        const secs = (elapsed % 60).toFixed(1).padStart(4, '0');
        shotClockTimer.textContent = `00:${mins}:${secs}`;
    }, 100);

    // --------------------------------------------------------------------------
    // WebSocket Telemetry Ingestion
    // --------------------------------------------------------------------------
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/telemetry`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => console.log("OmniDirector Studio Connected");

        ws.onmessage = (event) => {
            const t = JSON.parse(event.data);
            handleTelemetry(t);
        };

        ws.onclose = () => setTimeout(connectWebSocket, 2000);
    }

    function handleTelemetry(t) {
        if (t.active_camera_id !== activeCameraId) {
            activeCameraId = t.active_camera_id;
            shotStartTime = Date.now();
            updateCameraActiveState();
            addTimelineMarker(t.latest_decision && t.latest_decision.is_climax_highlight);
        }

        activeProviderLabel.textContent = t.active_provider_name;
        statTotalCuts.textContent = t.total_cuts_made;
        statHighlights.textContent = t.climax_highlights_count;
        statKineticCrop.textContent = t.kinetic_crop_x.toFixed(2);

        // Speech & Subtitles
        if (t.latest_transcription) {
            subtitleSpeaker.textContent = t.latest_transcription.speaker_id.toUpperCase();
            subtitleText.textContent = t.latest_transcription.text;
            detectedEmotionsTag.textContent = t.latest_transcription.detected_emotions.join(', ') || 'Focused';

            const energyPct = Math.round(t.latest_transcription.energy_score * 100);
            vuFill.style.width = `${energyPct}%`;

            // Vertical Reel Captions
            if (t.latest_transcription.words && t.latest_transcription.words.length > 0) {
                const words = t.latest_transcription.words.slice(0, 5);
                reelCaptions.innerHTML = words.map((w, idx) => 
                    `<span class="caption-token ${idx === words.length - 1 ? 'active-token' : ''}">${w.word}</span>`
                ).join(' ');
            }
        }

        // SAM 3.1 Masks
        if (t.latest_sam_segmentation) {
            samLatencyTag.textContent = `${t.latest_sam_segmentation.latency_ms}ms`;
            currentMasks = t.latest_sam_segmentation.masks || [];

            samMasksList.innerHTML = currentMasks.map(m => `
                <div class="mask-row-item">
                    <div class="mask-label-group">
                        <span class="mask-dot"></span>
                        <span>${m.label}</span>
                    </div>
                    <span class="mask-score">${(m.confidence * 100).toFixed(1)}%</span>
                </div>
            `).join('');
        }

        // Kinetic Centering
        if (t.kinetic_crop_x !== undefined) {
            kineticX = t.kinetic_crop_x;
            kineticY = t.kinetic_crop_y;
        }

        // Muse Spark Reasoning
        if (t.latest_decision) {
            reasoningBubble.textContent = t.latest_decision.reasoning;
            reasoningModelTag.textContent = t.latest_decision.model_version;
            reasoningConfidence.textContent = `Confidence: ${(t.latest_decision.confidence * 100).toFixed(0)}%`;

            if (t.latest_decision.is_climax_highlight) {
                climaxTint.classList.add('active');
                setTimeout(() => climaxTint.classList.remove('active'), 500);
            }
        }

        // Cuts Feed
        if (t.recent_cuts_history) {
            cutsFeed.innerHTML = t.recent_cuts_history.map(c => `
                <li class="cut-feed-item">
                    <div class="cut-feed-top">
                        <span class="cut-cam-name">${c.camera}</span>
                        <span class="cut-time-label">${c.timestamp} • ${c.type}</span>
                    </div>
                    <p class="cut-feed-reason">${c.reason}</p>
                </li>
            `).join('');
        }
    }

    function addTimelineMarker(isClimax) {
        const mark = document.createElement('div');
        mark.className = `timeline-cut-mark ${isClimax ? 'climax' : ''}`;
        const pct = Math.floor(Math.random() * 85) + 5;
        mark.style.left = `${pct}%`;
        timelineMarkersLayer.appendChild(mark);
        if (timelineMarkersLayer.children.length > 25) {
            timelineMarkersLayer.removeChild(timelineMarkersLayer.firstChild);
        }
    }

    loadConfig();
    connectWebSocket();
});
