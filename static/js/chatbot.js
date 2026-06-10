// ============================================================
// CHATBOT INTELIGENTE POMALCA — Anthropic Claude
// ============================================================

let chatbotAbierto = false;
let esperando = false;
const historial = [];  // { role: 'user'|'assistant', content: string }

function toggleChatbot() {
    chatbotAbierto = !chatbotAbierto;
    const panel  = document.getElementById('chatbot-panel');
    const toggle = document.getElementById('chatbot-toggle');

    if (chatbotAbierto) {
        panel.classList.add('chatbot-open');
        toggle.classList.add('chatbot-active');
        if (document.getElementById('chatbot-messages').children.length === 0) {
            _agregarBot('¡Hola! Soy el asistente de Pomalca. Puedo orientarte sobre solicitudes, maquinaria, actividades, roles y más. ¿En qué te ayudo?');
        }
        setTimeout(() => document.getElementById('chatbot-input').focus(), 200);
    } else {
        panel.classList.remove('chatbot-open');
        toggle.classList.remove('chatbot-active');
    }
}

// ---- Renderizado de mensajes ----

function _agregarBot(html) {
    const cont = document.getElementById('chatbot-messages');
    const div  = document.createElement('div');
    div.className = 'chatbot-msg msg-bot';
    div.innerHTML = `<div class="chatbot-bubble">${html}</div>`;
    cont.appendChild(div);
    cont.scrollTop = cont.scrollHeight;
}

function _agregarUsuario(texto) {
    const cont = document.getElementById('chatbot-messages');
    const div  = document.createElement('div');
    div.className = 'chatbot-msg msg-user';
    div.innerHTML = `<div class="chatbot-bubble">${_escapeHtml(texto)}</div>`;
    cont.appendChild(div);
    cont.scrollTop = cont.scrollHeight;
}

function _mostrarTyping() {
    const cont = document.getElementById('chatbot-messages');
    const div  = document.createElement('div');
    div.id = 'chatbot-typing';
    div.className = 'chatbot-msg msg-bot';
    div.innerHTML = `<div class="chatbot-bubble typing-indicator"><span></span><span></span><span></span></div>`;
    cont.appendChild(div);
    cont.scrollTop = cont.scrollHeight;
}

function _ocultarTyping() {
    const el = document.getElementById('chatbot-typing');
    if (el) el.remove();
}

function _escapeHtml(txt) {
    return txt.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ---- Envío de mensajes ----

async function enviarMensaje() {
    const input = document.getElementById('chatbot-input');
    const texto = input.value.trim();
    if (!texto || esperando) return;

    input.value = '';
    input.style.height = 'auto';
    document.getElementById('chatbot-send').disabled = true;
    document.getElementById('chatbot-quick-replies').style.display = 'none';

    _agregarUsuario(texto);
    historial.push({ role: 'user', content: texto });

    esperando = true;
    _mostrarTyping();

    try {
        const res = await fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mensaje: texto, historial })
        });
        const data = await res.json();
        _ocultarTyping();

        const respuesta = data.respuesta || 'No pude procesar tu consulta. Intenta de nuevo.';
        historial.push({ role: 'assistant', content: respuesta });
        _agregarBot(respuesta);

    } catch (e) {
        _ocultarTyping();
        _agregarBot('Error de conexión. Revisa tu conexión e intenta de nuevo.');
    } finally {
        esperando = false;
        document.getElementById('chatbot-send').disabled = false;
        input.focus();
    }
}

function enviarRapido(texto) {
    document.getElementById('chatbot-input').value = texto;
    enviarMensaje();
}

function manejarTecla(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        enviarMensaje();
    }
    const ta = document.getElementById('chatbot-input');
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 90) + 'px';
}
