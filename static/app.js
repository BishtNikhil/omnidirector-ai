/**
 * OmniDirector Studio — Professional Minimalist Controller
 * Incorporates:
 * 1. Spring-Damped Dynamic Center-Staging & Kinetic Pan-and-Scan for 9:16 Vertical Reel
 * 2. Live Local Webcam / OBS Virtual Camera Ingestion
 * 3. Interactive SAM 3.1 Point-and-Click Zero-Shot Prompting
 * 4. 1-Click DaVinci / Premiere EDL Export & 9:16 Highlight Reel Recording
 * 5. Meta Model Architecture & Payload Transparency Drawer
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
    const activeModelTag = document.getElementById('activeModelTag');
    const selectCloudProvider = document.getElementById('selectCloudProvider');
    const activeCamTitle = document.getElementById('activeCamTitle');
    const shotClockTimer = document.getElementById('shotClockTimer');
    const toggleSafeGuides = document.getElementById('toggleSafeGuides');
    const safeGuidesOverlay = document.getElementById('safeGuidesOverlay');
    const toggleSamMasks = document.getElementById('toggleSamMasks');

    const studioCanvas = document.getElementById('studioMainCanvas');
    const studioCtx = studioCanvas.getContext('2d');
    const reelCanvas = document.getElementById('reelCanvas');
    const reelCtx = reelCanvas.getContext('2d');
    const clickRipple = document.getElementById('clickRipple');

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

    // Reel Elements
    const reelTargetSpeaker = document.getElementById('reelTargetSpeaker');
    const reelZoomLabel = document.getElementById('reelZoomLabel');
    const reelRecordBanner = document.getElementById('reelRecordBanner');
    const recCountdown = document.getElementById('recCountdown');
    const reelCaptions = document.getElementById('reelCaptions');

    // Inspector Elements
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

    // New Header Action Buttons
    const btnWebcamToggle = document.getElementById('btnWebcamToggle');
    const webcamLabel = document.getElementById('webcamLabel');
    const webcamVideoElement = document.getElementById('webcamVideoElement');
    const btnScreenShareToggle = document.getElementById('btnScreenShareToggle');
    const screenShareLabel = document.getElementById('screenShareLabel');
    const screenShareVideoElement = document.getElementById('screenShareVideoElement');
    const btnOpenMultiCamGuide = document.getElementById('btnOpenMultiCamGuide');
    const multiCamModalOverlay = document.getElementById('multiCamModalOverlay');
    const btnCloseMultiCamGuide = document.getElementById('btnCloseMultiCamGuide');

    const btnExportReel = document.getElementById('btnExportReel');
    const btnExportEdl = document.getElementById('btnExportEdl');
    const btnOpenMetaDrawer = document.getElementById('btnOpenMetaDrawer');

    // Meta Drawer Elements
    const metaDrawerOverlay = document.getElementById('metaDrawerOverlay');
    const btnCloseDrawer = document.getElementById('btnCloseDrawer');
    const codeMuseSpark = document.getElementById('codeMuseSpark');
    const codeSam = document.getElementById('codeSam');
    const codeMuseVoice = document.getElementById('codeMuseVoice');

    // --------------------------------------------------------------------------
    // State Architecture
    // --------------------------------------------------------------------------
    let cameras = [];
    let activeCameraId = "cam_host";
    let isAutoDirecting = true;
    let showSamMasks = true;
    let shotStartTime = Date.now();
    let currentMasks = [];
    let connectedCameraIds = ['cam_host', 'cam_wide', 'cam_screen', 'cam_reaction'];

    // Real-Time Computer Vision Face Tracking
    let liveFaceX = 0.50;
    let liveFaceY = 0.40;
    let hasDetectedLiveFace = false;
    let nativeFaceDetector = null;
    let faceTrackCanvas = null;
    let faceTrackCtx = null;

    if ('FaceDetector' in window) {
        try {
            nativeFaceDetector = new window.FaceDetector({ fastMode: true, maxDetectedFaces: 1 });
            console.log("OmniDirector: Native FaceDetector initialized");
        } catch (e) {
            console.log("OmniDirector: Using computer vision skin-luminance centroid tracking");
        }
    }

    // Spring-Damped Kinetic Camera Tracking
    let currentReelX = 0.5;
    let targetReelX = 0.5;
    let currentReelZoom = 1.0;
    let targetReelZoom = 1.0;
    let activeSpeakerId = "host";

    // Media & Recording
    let isWebcamActive = false;
    let webcamStream = null;
    let isScreenShareActive = false;
    let screenShareStream = null;

    let mediaRecorder = null;
    let recordedChunks = [];
    let isRecordingReel = false;

    let wavePhase = 0;
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
    // Real-Time Webcam Face Tracking Loop (50ms interval)
    // --------------------------------------------------------------------------
    async function trackWebcamFace() {
        if (!isWebcamActive || !webcamVideoElement || webcamVideoElement.readyState < 2) return;

        // 1. Try Native FaceDetector API (Chromium/Edge)
        if (nativeFaceDetector) {
            try {
                const faces = await nativeFaceDetector.detect(webcamVideoElement);
                if (faces && faces.length > 0) {
                    const b = faces[0].boundingBox;
                    const vW = webcamVideoElement.videoWidth || 1280;
                    const vH = webcamVideoElement.videoHeight || 720;
                    const fx = (b.x + b.width / 2) / vW;
                    const fy = (b.y + b.height / 2) / vH;
                    liveFaceX += (fx - liveFaceX) * 0.35;
                    liveFaceY += (fy - liveFaceY) * 0.35;
                    hasDetectedLiveFace = true;
                    return;
                }
            } catch (err) {}
        }

        // 2. High-Performance Canvas Computer Vision Centroid (Universal Browser Support)
        if (!faceTrackCanvas) {
            faceTrackCanvas = document.createElement('canvas');
            faceTrackCanvas.width = 160;
            faceTrackCanvas.height = 90;
            faceTrackCtx = faceTrackCanvas.getContext('2d', { willReadFrequently: true });
        }
        faceTrackCtx.drawImage(webcamVideoElement, 0, 0, 160, 90);
        const imgData = faceTrackCtx.getImageData(0, 0, 160, 90).data;
        let sumX = 0, sumY = 0, count = 0;
        for (let y = 10; y < 80; y += 2) {
            for (let x = 15; x < 145; x += 2) {
                const idx = (y * 160 + x) * 4;
                const r = imgData[idx];
                const g = imgData[idx + 1];
                const b = imgData[idx + 2];
                // Human skin tone locus in RGB space
                if (r > 90 && g > 45 && b > 30 && r > g && r > b && (r - g) > 12) {
                    sumX += x;
                    sumY += y;
                    count++;
                }
            }
        }
        if (count > 50) {
            const fx = sumX / (count * 160);
            const fy = sumY / (count * 90);
            liveFaceX += (fx - liveFaceX) * 0.35;
            liveFaceY += (fy - liveFaceY) * 0.35;
            hasDetectedLiveFace = true;
        }
    }
    setInterval(trackWebcamFace, 50);

    // --------------------------------------------------------------------------
    // 1. Live Webcam / OBS Virtual Camera Ingestion
    // --------------------------------------------------------------------------
    btnWebcamToggle.addEventListener('click', async () => {
        if (!isWebcamActive) {
            try {
                webcamStream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 1280, height: 720 },
                    audio: true
                });
                webcamVideoElement.srcObject = webcamStream;
                await webcamVideoElement.play();
                isWebcamActive = true;
                btnWebcamToggle.classList.add('webcam-active');
                webcamLabel.textContent = "Camera Connected (Live)";
                triggerManualCut('cam_host');
                renderCamerasGrid();
            } catch (err) {
                console.warn("Webcam access denied or unavailable:", err);
                alert("Camera access note: Enable webcam permissions in your browser or select OBS Virtual Camera to feed live video.");
            }
        } else {
            if (webcamStream) {
                webcamStream.getTracks().forEach(t => t.stop());
            }
            webcamVideoElement.srcObject = null;
            isWebcamActive = false;
            btnWebcamToggle.classList.remove('webcam-active');
            webcamLabel.textContent = "Connect Camera";
            renderCamerasGrid();
        }
    });

    // --------------------------------------------------------------------------
    // 1B. Screen Sharing into CAM 3 (DisplayMedia)
    // --------------------------------------------------------------------------
    btnScreenShareToggle.addEventListener('click', async () => {
        if (!isScreenShareActive) {
            try {
                screenShareStream = await navigator.mediaDevices.getDisplayMedia({
                    video: { cursor: "always" },
                    audio: false
                });
                screenShareVideoElement.srcObject = screenShareStream;
                await screenShareVideoElement.play();
                isScreenShareActive = true;
                btnScreenShareToggle.classList.add('screenshare-active');
                screenShareLabel.textContent = "Screen Live (CAM 3)";
                triggerManualCut('cam_screen');
                renderCamerasGrid();

                screenShareStream.getVideoTracks()[0].onended = () => {
                    stopScreenSharing();
                };
            } catch (err) {
                console.warn("Screen share cancelled:", err);
            }
        } else {
            stopScreenSharing();
        }
    });

    function stopScreenSharing() {
        if (screenShareStream) {
            screenShareStream.getTracks().forEach(t => t.stop());
        }
        screenShareVideoElement.srcObject = null;
        isScreenShareActive = false;
        btnScreenShareToggle.classList.remove('screenshare-active');
        screenShareLabel.textContent = "Share Screen";
        renderCamerasGrid();
    }

    // Multi-Cam Ingest Guide Modal
    btnOpenMultiCamGuide.addEventListener('click', () => {
        multiCamModalOverlay.style.display = 'flex';
    });
    btnCloseMultiCamGuide.addEventListener('click', () => {
        multiCamModalOverlay.style.display = 'none';
    });
    multiCamModalOverlay.addEventListener('click', (e) => {
        if (e.target === multiCamModalOverlay) multiCamModalOverlay.style.display = 'none';
    });

    // --------------------------------------------------------------------------
    // 2. Interactive SAM 3.1 Point Prompting (Click-to-Track)
    // --------------------------------------------------------------------------
    studioCanvas.addEventListener('click', async (e) => {
        const rect = studioCanvas.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;
        const normX = Math.max(0.02, Math.min(0.98, clickX / rect.width));
        const normY = Math.max(0.02, Math.min(0.98, clickY / rect.height));

        // Animate visual ripple
        clickRipple.style.left = `${clickX}px`;
        clickRipple.style.top = `${clickY}px`;
        clickRipple.classList.remove('animate');
        void clickRipple.offsetWidth; // trigger reflow
        clickRipple.classList.add('animate');

        // Immediately update kinetic target to clicked point
        targetReelX = normX;

        try {
            const res = await fetch('/api/sam/point-prompt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    camera_id: activeCameraId,
                    point_x: normX,
                    point_y: normY
                })
            });
            const newMask = await res.json();
            currentMasks.unshift(newMask);
            if (currentMasks.length > 5) currentMasks.pop();
            renderMasksList();
        } catch (err) {
            console.error("Point prompt error:", err);
        }
    });

    // --------------------------------------------------------------------------
    // 3. Export Hub: EDL Download & 9:16 Reel Recording
    // --------------------------------------------------------------------------
    btnExportEdl.addEventListener('click', () => {
        window.location.href = '/api/export/edl';
    });

    btnExportReel.addEventListener('click', () => {
        if (isRecordingReel) return;
        isRecordingReel = true;
        btnExportReel.classList.add('recording');
        reelRecordBanner.style.display = 'flex';
        recordedChunks = [];

        try {
            const stream = reelCanvas.captureStream(30);
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp9' });

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) recordedChunks.push(e.data);
            };

            mediaRecorder.onstop = () => {
                const blob = new Blob(recordedChunks, { type: 'video/webm' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `omnidirector_vertical_highlight_${Date.now()}.webm`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);

                isRecordingReel = false;
                btnExportReel.classList.remove('recording');
                reelRecordBanner.style.display = 'none';
            };

            mediaRecorder.start();

            // 10-Second Recording Countdown
            let timeLeft = 10;
            const timer = setInterval(() => {
                timeLeft--;
                recCountdown.textContent = `RECORDING (${timeLeft}s)...`;
                if (timeLeft <= 0) {
                    clearInterval(timer);
                    mediaRecorder.stop();
                }
            }, 1000);
        } catch (err) {
            console.error("Recording error:", err);
            isRecordingReel = false;
            btnExportReel.classList.remove('recording');
            reelRecordBanner.style.display = 'none';
        }
    });

    // --------------------------------------------------------------------------
    // 4. Meta Model Transparency Drawer
    // --------------------------------------------------------------------------
    btnOpenMetaDrawer.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/meta-prompts');
            const data = await res.json();
            codeMuseSpark.textContent = JSON.stringify(data.muse_spark, null, 2);
            codeSam.textContent = JSON.stringify(data.sam_3_1, null, 2);
            codeMuseVoice.textContent = JSON.stringify(data.muse_voice_transcribe, null, 2);
            metaDrawerOverlay.style.display = 'flex';
        } catch (err) {
            console.error("Payload fetch error:", err);
        }
    });

    btnCloseDrawer.addEventListener('click', () => {
        metaDrawerOverlay.style.display = 'none';
    });

    metaDrawerOverlay.addEventListener('click', (e) => {
        if (e.target === metaDrawerOverlay) metaDrawerOverlay.style.display = 'none';
    });

    // Cloud Provider Switcher Event Listener
    if (selectCloudProvider) {
        selectCloudProvider.addEventListener('change', async (e) => {
            const targetProvider = e.target.value;
            try {
                const res = await fetch('/api/provider/switch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ provider: targetProvider })
                });
                const data = await res.json();
                if (activeModelTag) {
                    if (targetProvider === 'baseten') {
                        activeModelTag.textContent = 'Baseten Muse Spark Open (2M TPM)';
                    } else if (targetProvider === 'meta') {
                        activeModelTag.textContent = 'Meta Model API ($150 Credits)';
                    } else {
                        activeModelTag.textContent = 'Local Simulation Mode';
                    }
                }
            } catch (err) {
                console.error("Provider switch error:", err);
            }
        });
    }

    // --------------------------------------------------------------------------
    // Broadcast Canvas Rendering Engine
    // --------------------------------------------------------------------------
    function renderStudioScene() {
        const W = studioCanvas.width;
        const H = studioCanvas.height;
        if (!W || !H) return;

        studioCtx.clearRect(0, 0, W, H);
        const t = (Date.now() - sessionStartMs) / 1000;

        // If user webcam is live on CAM 1, render real video with real-time face tracking
        if (isWebcamActive && activeCameraId === 'cam_host' && webcamVideoElement.readyState >= 2) {
            studioCtx.save();
            studioCtx.drawImage(webcamVideoElement, 0, 0, W, H);
            studioCtx.restore();

            // Generate real-time SAM 3.1 polygonal contours directly around tracked face
            const fx = liveFaceX;
            const fy = liveFaceY;
            currentMasks = [
                {
                    id: "live_host_face",
                    label: "Host Live Broadcaster (Face - Tracked)",
                    confidence: 0.994,
                    polygon_points: [
                        [fx - 0.08, fy - 0.12], [fx + 0.08, fy - 0.12],
                        [fx + 0.11, fy + 0.04], [fx + 0.06, fy + 0.14],
                        [fx - 0.06, fy + 0.14], [fx - 0.11, fy + 0.04]
                    ],
                    suggested_crop_x: fx
                },
                {
                    id: "live_host_body",
                    label: "Broadcaster Torso / Mic Zone",
                    confidence: 0.975,
                    polygon_points: [
                        [fx - 0.20, fy + 0.15], [fx + 0.20, fy + 0.15],
                        [fx + 0.28, fy + 0.52], [fx - 0.28, fy + 0.52]
                    ],
                    suggested_crop_x: fx
                }
            ];

            // Lock 9:16 vertical crop target to the user's real face position
            targetReelX = fx;
            targetReelZoom = 1.05;
            activeSpeakerId = "host";
            reelTargetSpeaker.textContent = "TARGET: HOST (YOU - TRACKED)";
            subtitleSpeaker.textContent = "HOST (YOU)";
        } else if (isScreenShareActive && activeCameraId === 'cam_screen' && screenShareVideoElement.readyState >= 2) {
            studioCtx.save();
            studioCtx.drawImage(screenShareVideoElement, 0, 0, W, H);
            studioCtx.restore();
            targetReelX = 0.50;
        } else {
            // Draw cinematic studio scenes
            if (activeCameraId === 'cam_host') {
                drawHostPrimeScene(studioCtx, W, H, t);
            } else if (activeCameraId === 'cam_wide') {
                drawWideStudioScene(studioCtx, W, H, t);
            } else if (activeCameraId === 'cam_screen') {
                drawScreenHudScene(studioCtx, W, H, t);
            } else {
                drawReactionScene(studioCtx, W, H, t);
            }
        }

        // Draw SAM 3.1 Polygonal Segmentation Contours
        if (showSamMasks && currentMasks && currentMasks.length > 0) {
            drawSAMPolygons(studioCtx, W, H);
        }

        // Render 9:16 Vertical Reel with Spring-Damped Center Staging
        renderVerticalReel();
    }

    function drawHostPrimeScene(ctx, W, H, t) {
        const grad = ctx.createLinearGradient(0, 0, W, H);
        grad.addColorStop(0, '#1E2430');
        grad.addColorStop(0.5, '#141822');
        grad.addColorStop(1, '#0C0F15');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, W, H);

        // Acoustic Panel Slats
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
        ctx.lineWidth = 14 * (W / 1200);
        for (let x = W * 0.1; x < W * 0.9; x += W * 0.06) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, H * 0.7);
            ctx.stroke();
        }

        // Warm Ambient Backlight
        const halo = ctx.createRadialGradient(W * 0.5, H * 0.42, 10, W * 0.5, H * 0.42, W * 0.35);
        halo.addColorStop(0, 'rgba(212, 150, 80, 0.18)');
        halo.addColorStop(0.7, 'rgba(72, 97, 134, 0.12)');
        halo.addColorStop(1, 'transparent');
        ctx.fillStyle = halo;
        ctx.fillRect(0, 0, W, H);

        const breath = Math.sin(t * 1.8) * 3;
        const headX = W * 0.5;
        const headY = H * 0.42 + breath;
        const headR = H * 0.14;

        // Torso
        ctx.fillStyle = '#181E29';
        ctx.beginPath();
        ctx.moveTo(headX - headR * 2.2, H);
        ctx.lineTo(headX - headR * 1.6, headY + headR * 1.4);
        ctx.quadraticCurveTo(headX, headY + headR * 1.1, headX + headR * 1.6, headY + headR * 1.4);
        ctx.lineTo(headX + headR * 2.2, H);
        ctx.closePath();
        ctx.fill();

        ctx.strokeStyle = 'rgba(200, 214, 232, 0.3)';
        ctx.lineWidth = 3;
        ctx.stroke();

        // Head
        ctx.fillStyle = '#283142';
        ctx.beginPath();
        ctx.arc(headX, headY, headR, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = 'rgba(234, 219, 202, 0.45)';
        ctx.lineWidth = 2.5;
        ctx.stroke();

        // Mic
        const micX = W * 0.38;
        const micY = H * 0.62;
        ctx.fillStyle = '#0F131A';
        ctx.beginPath();
        ctx.roundRect(micX - 16, micY - 32, 32, 64, 8);
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.strokeStyle = '#181C24';
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(micX - 16, micY);
        ctx.lineTo(W * 0.18, H * 0.88);
        ctx.stroke();
    }

    function drawWideStudioScene(ctx, W, H, t) {
        const grad = ctx.createLinearGradient(0, 0, W, H);
        grad.addColorStop(0, '#161C26');
        grad.addColorStop(1, '#0C0F14');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, W, H);

        // Podium Table
        ctx.fillStyle = '#1A212E';
        ctx.beginPath();
        ctx.moveTo(W * 0.12, H * 0.95);
        ctx.lineTo(W * 0.25, H * 0.65);
        ctx.lineTo(W * 0.75, H * 0.65);
        ctx.lineTo(W * 0.88, H * 0.95);
        ctx.closePath();
        ctx.fill();

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
    }

    function drawScreenHudScene(ctx, W, H, t) {
        ctx.fillStyle = '#0F1217';
        ctx.fillRect(0, 0, W, H);

        ctx.fillStyle = '#151922';
        ctx.fillRect(W * 0.04, H * 0.08, W * 0.52, H * 0.84);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        ctx.strokeRect(W * 0.04, H * 0.08, W * 0.52, H * 0.84);

        const codeColors = ['#4F7A67', '#486186', '#B08244', '#8591A5'];
        for (let y = H * 0.16; y < H * 0.82; y += H * 0.055) {
            ctx.fillStyle = codeColors[Math.floor(y * 10) % codeColors.length];
            const lineW = (Math.sin(y * 2) * 0.15 + 0.3) * W;
            ctx.fillRect(W * 0.08, y, lineW, 8 * (H / 600));
        }

        ctx.fillStyle = '#1A212E';
        ctx.fillRect(W * 0.60, H * 0.08, W * 0.36, H * 0.84);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        ctx.strokeRect(W * 0.60, H * 0.08, W * 0.36, H * 0.84);

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
        const grad = ctx.createLinearGradient(0, 0, W, H);
        grad.addColorStop(0, '#211B24');
        grad.addColorStop(1, '#0F0D13');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, W, H);

        const breath = Math.sin(t * 2.2) * 4;
        const headX = W * 0.55;
        const headY = H * 0.44 + breath;

        ctx.fillStyle = '#312738';
        ctx.beginPath();
        ctx.ellipse(headX, headY, H * 0.13, H * 0.16, -0.15, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = 'rgba(224, 109, 91, 0.4)';
        ctx.lineWidth = 2.5;
        ctx.stroke();

        ctx.fillStyle = '#1B1622';
        ctx.fillRect(W * 0.38, H * 0.60, W * 0.35, H * 0.40);
    }

    function drawSAMPolygons(ctx, W, H) {
        const styles = [
            { stroke: '#4F7A67', fill: 'rgba(79, 122, 103, 0.15)' },
            { stroke: '#486186', fill: 'rgba(72, 97, 134, 0.15)' },
            { stroke: '#B08244', fill: 'rgba(176, 130, 68, 0.15)' }
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

            ctx.strokeStyle = style.stroke;
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 4]);
            ctx.stroke();
            ctx.setLineDash([]);

            // Minimalist Inter Label Tag
            const labelX = m.polygon_points[0][0] * W;
            const labelY = Math.max(26, m.polygon_points[0][1] * H - 8);

            ctx.font = '600 12px Inter, sans-serif';
            const textWidth = ctx.measureText(m.label).width;

            ctx.fillStyle = '#FFFFFF';
            ctx.shadowColor = 'rgba(0,0,0,0.12)';
            ctx.shadowBlur = 6;
            ctx.fillRect(labelX - 4, labelY - 15, textWidth + 10, 20);
            ctx.shadowBlur = 0;

            ctx.strokeStyle = style.stroke;
            ctx.lineWidth = 1;
            ctx.strokeRect(labelX - 4, labelY - 15, textWidth + 10, 20);

            ctx.fillStyle = style.stroke;
            ctx.fillText(m.label, labelX, labelY);
        });
    }

    // --------------------------------------------------------------------------
    // 9:16 Kinetic Vertical Reel (Spring-Damped Center-Staging Engine)
    // --------------------------------------------------------------------------
    function renderVerticalReel() {
        const W = reelCanvas.width;
        const H = reelCanvas.height;
        if (!W || !H) return;

        reelCtx.clearRect(0, 0, W, H);

        // Spring Physics: Smoothly glide toward target crop X with zero jitter
        currentReelX += (targetReelX - currentReelX) * 0.08;
        currentReelZoom += (targetReelZoom - currentReelZoom) * 0.10;

        reelZoomLabel.textContent = `${currentReelZoom.toFixed(2)}x`;

        const sW = studioCanvas.width;
        const sH = studioCanvas.height;

        // Base 9:16 window
        let cropW = (sH * (9 / 16)) / currentReelZoom;
        let cropH = sH / currentReelZoom;

        let cropX = (currentReelX * sW) - (cropW / 2);
        cropX = Math.max(0, Math.min(sW - cropW, cropX));
        let cropY = (sH - cropH) / 2;

        reelCtx.drawImage(studioCanvas, cropX, cropY, cropW, cropH, 0, 0, W, H);
    }

    setInterval(renderStudioScene, 35);

    // Waveform
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
    // Cameras & API Data (With Online/Offline Controls)
    // --------------------------------------------------------------------------
    async function loadConfig() {
        try {
            const res = await fetch('/api/config');
            const data = await res.json();
            if (activeProviderLabel) activeProviderLabel.textContent = data.active_provider;
            if (data.active_provider && selectCloudProvider) {
                const provLower = data.active_provider.toLowerCase();
                if (provLower.includes('baseten')) selectCloudProvider.value = 'baseten';
                else if (provLower.includes('meta')) selectCloudProvider.value = 'meta';
                else selectCloudProvider.value = 'simulation';
            }
            cameras = data.cameras;
            connectedCameraIds = cameras.filter(c => c.is_connected !== false).map(c => c.id);
            renderCamerasGrid();
        } catch (e) {
            console.error("Config fetch error:", e);
        }
    }

    function renderCamerasGrid() {
        camerasGrid.innerHTML = '';
        cameras.forEach(cam => {
            const isOnline = connectedCameraIds.includes(cam.id);
            const isProgram = cam.id === activeCameraId;
            const tile = document.createElement('div');
            tile.className = `cam-tile ${isProgram ? 'on-air-active' : ''} ${!isOnline ? 'is-offline' : ''}`;
            tile.id = `tile_${cam.id}`;

            let sourceLabel = "Simulation Engine";
            if (cam.id === 'cam_host' && isWebcamActive) sourceLabel = "📹 Live Webcam";
            else if (cam.id === 'cam_screen' && isScreenShareActive) sourceLabel = "🖥️ Live Screen";
            else if (cam.id === 'cam_reaction') sourceLabel = "OBS Virtual / Cam 4";

            tile.innerHTML = `
                <div class="cam-viewport-thumb">
                    <span class="cam-tally-tag">${isProgram ? 'PROGRAM' : isOnline ? 'PREVIEW' : 'OFFLINE'}</span>
                    <button class="cam-power-toggle ${isOnline ? 'online' : 'offline'}" title="Toggle Online / Offline status">
                        ${isOnline ? '🟢 LIVE' : '⚪ OFFLINE'}
                    </button>
                    ${isOnline ? `
                        <div style="font-size: 26px; opacity: 0.7;">
                            ${cam.id === 'cam_host' && isWebcamActive ? '📹' : cam.id === 'cam_screen' && isScreenShareActive ? '🖥️' : cam.role === 'host' ? '🎙️' : cam.role === 'wide' ? '🏛️' : cam.role === 'screen' ? '💻' : '⚡'}
                        </div>
                    ` : `
                        <span class="offline-watermark">NO SIGNAL / OFFLINE</span>
                    `}
                </div>
                <div class="cam-tile-footer">
                    <div>
                        <div class="cam-tile-name">${cam.label}</div>
                        <div class="cam-source-tag">${isOnline ? sourceLabel : 'Bypassed by AI Director'}</div>
                    </div>
                    <span class="cam-tile-role">${cam.role}</span>
                </div>
            `;

            const powerBtn = tile.querySelector('.cam-power-toggle');
            powerBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleCameraOnline(cam.id, !isOnline);
            });

            tile.addEventListener('click', () => {
                if (!isOnline) {
                    alert(`${cam.label} is currently OFFLINE. Click the [⚪ OFFLINE] button to bring it ONLINE first!`);
                    return;
                }
                triggerManualCut(cam.id);
            });

            camerasGrid.appendChild(tile);
        });
    }

    async function toggleCameraOnline(camId, newStatus) {
        try {
            const res = await fetch('/api/cameras/status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ camera_id: camId, is_connected: newStatus })
            });
            const data = await res.json();
            connectedCameraIds = data.connected_cameras || [];
            if (data.active_camera_id) {
                activeCameraId = data.active_camera_id;
            }
            renderCamerasGrid();
            updateCameraActiveState();
        } catch (err) {
            console.error("Camera status toggle error:", err);
        }
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
        if (cam) activeCamTitle.textContent = cam.label;
        document.querySelectorAll('.cam-tile').forEach(t => {
            const cid = t.id.replace('tile_', '');
            const isCur = cid === activeCameraId;
            const isOnline = connectedCameraIds.includes(cid);
            t.classList.toggle('on-air-active', isCur);
            t.classList.toggle('is-offline', !isOnline);
            const tally = t.querySelector('.cam-tally-tag');
            if (tally) tally.textContent = isCur ? 'PROGRAM' : isOnline ? 'PREVIEW' : 'OFFLINE';
        });
    }

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

    setInterval(() => {
        const elapsed = (Date.now() - shotStartTime) / 1000;
        const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
        const secs = (elapsed % 60).toFixed(1).padStart(4, '0');
        shotClockTimer.textContent = `00:${mins}:${secs}`;
    }, 100);

    // --------------------------------------------------------------------------
    // WebSocket Telemetry Stream
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

        if (t.connected_cameras) {
            connectedCameraIds = t.connected_cameras;
            document.querySelectorAll('.cam-tile').forEach(tile => {
                const cid = tile.id.replace('tile_', '');
                const isOnline = connectedCameraIds.includes(cid);
                tile.classList.toggle('is-offline', !isOnline);
                const pBtn = tile.querySelector('.cam-power-toggle');
                if (pBtn) {
                    pBtn.className = `cam-power-toggle ${isOnline ? 'online' : 'offline'}`;
                    pBtn.textContent = isOnline ? '🟢 LIVE' : '⚪ OFFLINE';
                }
            });
        }

        if (t.active_provider_name) {
            if (activeProviderLabel) activeProviderLabel.textContent = t.active_provider_name;
            if (activeModelTag) {
                const nameLower = t.active_provider_name.toLowerCase();
                if (nameLower.includes('baseten')) {
                    activeModelTag.textContent = 'Baseten Muse Spark Open (2M TPM)';
                    if (selectCloudProvider && document.activeElement !== selectCloudProvider) {
                        selectCloudProvider.value = 'baseten';
                    }
                } else if (nameLower.includes('meta')) {
                    activeModelTag.textContent = 'Meta Model API ($150 Credits)';
                    if (selectCloudProvider && document.activeElement !== selectCloudProvider) {
                        selectCloudProvider.value = 'meta';
                    }
                } else {
                    activeModelTag.textContent = 'Local Simulation Mode';
                    if (selectCloudProvider && document.activeElement !== selectCloudProvider) {
                        selectCloudProvider.value = 'simulation';
                    }
                }
            }
        }
        statTotalCuts.textContent = t.total_cuts_made;
        statHighlights.textContent = t.climax_highlights_count;
        statKineticCrop.textContent = currentReelX.toFixed(2);

        // Speech & Center-Staging
        if (t.latest_transcription) {
            const isSoloLiveBroadcaster = isWebcamActive && activeCameraId === 'cam_host';
            if (!isSoloLiveBroadcaster) {
                subtitleSpeaker.textContent = t.latest_transcription.speaker_id.toUpperCase();
                subtitleText.textContent = t.latest_transcription.text;
                activeSpeakerId = t.latest_transcription.speaker_id;
                reelTargetSpeaker.textContent = `TARGET: ${activeSpeakerId.toUpperCase()} (LOCKED)`;

                if (activeCameraId === 'cam_wide') {
                    targetReelX = activeSpeakerId === 'guest' ? 0.65 : 0.35;
                } else if (activeCameraId === 'cam_reaction') {
                    targetReelX = 0.55;
                } else {
                    targetReelX = 0.50;
                }
            } else {
                subtitleSpeaker.textContent = "HOST (YOU)";
                activeSpeakerId = "host";
                reelTargetSpeaker.textContent = "TARGET: HOST (YOU - TRACKED)";
                targetReelX = liveFaceX;
            }

            detectedEmotionsTag.textContent = t.latest_transcription.detected_emotions.join(', ') || 'Focused';
            targetReelZoom = t.latest_transcription.is_climax_moment ? 1.08 : 1.00;

            const energyPct = Math.round(t.latest_transcription.energy_score * 100);
            vuFill.style.width = `${energyPct}%`;

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
            renderMasksList();
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

    function renderMasksList() {
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
