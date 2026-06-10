const MODELS_URL = 'https://cdn.jsdelivr.net/gh/justadudewhohacks/face-api.js@0.22.2/weights';

let camStream = null;
let previewInterval = null;
let modelosCargados = false;

async function inicializarCamara() {
    _setStatus('Cargando modelos de IA...', '');
    document.getElementById('btnActivar').disabled = true;

    try {
        if (!modelosCargados) {
            await Promise.all([
                faceapi.nets.tinyFaceDetector.loadFromUri(MODELS_URL),
                faceapi.nets.faceLandmark68TinyNet.loadFromUri(MODELS_URL),
                faceapi.nets.faceRecognitionNet.loadFromUri(MODELS_URL),
            ]);
            modelosCargados = true;
        }

        _setStatus('Activando cámara...', '');

        camStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480, facingMode: 'user' }
        });

        const video = document.getElementById('videoRegistro');
        video.srcObject = camStream;
        await video.play();

        document.getElementById('btnActivar').style.display = 'none';
        document.getElementById('btnCapturar').style.display = 'inline-block';
        document.getElementById('btnCapturar').disabled = false;
        document.getElementById('btnDetener').style.display = 'inline-block';

        _setStatus('Listo. Centra tu rostro y presiona "Capturar y Guardar Rostro".', '');
        _iniciarPreview();

    } catch (err) {
        _setStatus('Error al iniciar cámara: ' + (err.message || 'Sin acceso'), 'err');
        document.getElementById('btnActivar').disabled = false;
    }
}

function _iniciarPreview() {
    const video = document.getElementById('videoRegistro');
    const canvas = document.getElementById('canvasRegistro');

    previewInterval = setInterval(async () => {
        if (!video.videoWidth) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const deteccion = await faceapi
            .detectSingleFace(video, new faceapi.TinyFaceDetectorOptions())
            .withFaceLandmarks(true);

        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (deteccion) {
            const { x, y, width, height } = deteccion.detection.box;
            ctx.strokeStyle = '#27ae60';
            ctx.lineWidth = 3;
            ctx.strokeRect(x, y, width, height);
            document.getElementById('btnCapturar').disabled = false;
        } else {
            ctx.strokeStyle = 'rgba(231,76,60,0.6)';
            ctx.lineWidth = 2;
            ctx.setLineDash([8, 5]);
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            ctx.strokeRect(cx - 100, cy - 130, 200, 260);
            ctx.setLineDash([]);
        }
    }, 200);
}

async function capturarRostro() {
    const video = document.getElementById('videoRegistro');
    const btnCapturar = document.getElementById('btnCapturar');

    btnCapturar.disabled = true;
    _setStatus('Analizando rostro...', '');

    try {
        const deteccion = await faceapi
            .detectSingleFace(video, new faceapi.TinyFaceDetectorOptions())
            .withFaceLandmarks(true)
            .withFaceDescriptor();

        if (!deteccion) {
            _setStatus('No se detectó rostro. Centra tu cara e intenta de nuevo.', 'err');
            btnCapturar.disabled = false;
            return;
        }

        const descriptor = Array.from(deteccion.descriptor);

        const res = await fetch('/api/guardar_rostro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ descriptor })
        });
        const data = await res.json();

        if (data.code === 1) {
            _setStatus('Rostro registrado correctamente. Ya puedes iniciar sesion con tu cara.', 'ok');
            clearInterval(previewInterval);
            if (camStream) camStream.getTracks().forEach(t => t.stop());
            camStream = null;
            document.getElementById('btnCapturar').style.display = 'none';
            document.getElementById('btnDetener').style.display = 'none';
            document.getElementById('btnVolver').style.display = 'inline-block';
        } else {
            _setStatus((data.message || 'Error al guardar el rostro.'), 'err');
            btnCapturar.disabled = false;
        }
    } catch (e) {
        _setStatus('Error de conexión. Intenta de nuevo.', 'err');
        btnCapturar.disabled = false;
    }
}

function detenerCamara() {
    clearInterval(previewInterval);
    if (camStream) camStream.getTracks().forEach(t => t.stop());
    camStream = null;
    previewInterval = null;
    document.getElementById('btnActivar').style.display = 'inline-block';
    document.getElementById('btnActivar').disabled = false;
    document.getElementById('btnCapturar').style.display = 'none';
    document.getElementById('btnDetener').style.display = 'none';
    const canvas = document.getElementById('canvasRegistro');
    if (canvas) canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
    _setStatus('Cámara detenida. Presiona "Activar cámara" para reintentar.', '');
}

function _setStatus(msg, cls) {
    const el = document.getElementById('registroStatus');
    el.textContent = msg;
    el.className = 'face-reg-status' + (cls ? ' ' + cls : '');
}

window.addEventListener('beforeunload', () => {
    if (camStream) camStream.getTracks().forEach(t => t.stop());
});
