const MODELS_URL = 'https://cdn.jsdelivr.net/gh/justadudewhohacks/face-api.js@0.22.2/weights';

let camStream = null;
let scanInterval = null;
let estabilidad = 0;
let enviando = false;

async function abrirLoginFacial() {
    const modal = document.getElementById('modalFace');
    const status = document.getElementById('faceStatus');
    const btn = document.getElementById('btnLoginFacial');

    modal.classList.add('activo');
    btn.disabled = true;
    _setStatus('Cargando modelos de IA...', '');

    try {
        await Promise.all([
            faceapi.nets.tinyFaceDetector.loadFromUri(MODELS_URL),
            faceapi.nets.faceLandmark68TinyNet.loadFromUri(MODELS_URL),
            faceapi.nets.faceRecognitionNet.loadFromUri(MODELS_URL),
        ]);

        _setStatus('Activando cámara...', '');

        camStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480, facingMode: 'user' }
        });

        const video = document.getElementById('videoFace');
        video.srcObject = camStream;
        await video.play();

        estabilidad = 0;
        enviando = false;
        _setStatus('Centra tu rostro en el recuadro...', '');
        _iniciarEscaneo();

    } catch (err) {
        _setStatus('Error: ' + (err.message || 'Cámara no disponible'), 'err');
        btn.disabled = false;
    }
}

function _iniciarEscaneo() {
    const video = document.getElementById('videoFace');
    const canvas = document.getElementById('canvasFace');

    scanInterval = setInterval(async () => {
        if (enviando || !video.videoWidth) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const deteccion = await faceapi
            .detectSingleFace(video, new faceapi.TinyFaceDetectorOptions({ scoreThreshold: 0.5 }))
            .withFaceLandmarks(true)
            .withFaceDescriptor();

        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (deteccion) {
            const { x, y, width, height } = deteccion.detection.box;

            ctx.strokeStyle = '#27ae60';
            ctx.lineWidth = 3;
            ctx.strokeRect(x, y, width, height);

            estabilidad++;
            const pct = Math.min(Math.round((estabilidad / 12) * 100), 100);
            _setStatus(`Verificando identidad... ${pct}%`, '');

            if (estabilidad >= 12) {
                clearInterval(scanInterval);
                enviando = true;
                _setStatus('Identificando rostro...', '');
                await _verificarRostro(Array.from(deteccion.descriptor));
            }
        } else {
            estabilidad = 0;
            ctx.strokeStyle = 'rgba(231,76,60,0.6)';
            ctx.lineWidth = 2;
            ctx.setLineDash([8, 5]);
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            ctx.strokeRect(cx - 85, cy - 110, 170, 220);
            ctx.setLineDash([]);
            _setStatus('No se detectó rostro. Centra tu cara...', '');
        }
    }, 200);
}

async function _verificarRostro(descriptor) {
    try {
        const res = await fetch('/api/login_facial', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ descriptor })
        });
        const data = await res.json();

        if (data.code === 1) {
            _setStatus('Acceso concedido. Redirigiendo...', 'ok');
            _detenerCamara();
            setTimeout(() => { window.location.href = data.redirect; }, 1200);
        } else {
            _setStatus((data.message || 'Rostro no reconocido. Intenta de nuevo.'), 'err');
            setTimeout(() => {
                if (camStream) {
                    estabilidad = 0;
                    enviando = false;
                    _setStatus('Centra tu rostro e intenta de nuevo...', '');
                    _iniciarEscaneo();
                }
            }, 2500);
        }
    } catch (e) {
        _setStatus('Error de conexión. Intenta de nuevo.', 'err');
        enviando = false;
    }
}

function _detenerCamara() {
    if (scanInterval) clearInterval(scanInterval);
    if (camStream) camStream.getTracks().forEach(t => t.stop());
    scanInterval = null;
    camStream = null;
}

function cerrarModalFace() {
    _detenerCamara();
    document.getElementById('modalFace').classList.remove('activo');
    const canvas = document.getElementById('canvasFace');
    if (canvas) canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
    document.getElementById('btnLoginFacial').disabled = false;
}

function _setStatus(msg, cls) {
    const el = document.getElementById('faceStatus');
    el.textContent = msg;
    el.className = 'face-status-text' + (cls ? ' ' + cls : '');
}
