(function () {

    // ================================================================
    // BASE DE CONOCIMIENTO
    // ================================================================

    var REGLAS = [
        {
            palabras: ['hola', 'buenas', 'buenos', 'saludos', 'hey', 'hi'],
            respuesta: function () {
                return '¡Hola! Soy el asistente del Sistema de Gestión de Pomalca. Estoy aquí para ayudarte con el registro, inicio de sesión y el uso del sistema. ¿En qué puedo ayudarte?';
            }
        },
        {
            palabras: ['registr', 'crear cuenta', 'nueva cuenta', 'nuevo usuario', 'como entro', 'como accedo'],
            respuesta: function () {
                return 'Para registrarte en el sistema:\n\n1. Haz clic en "Registrarse" en la página de inicio\n2. Completa los campos obligatorios:\n   • DNI: exactamente 8 dígitos\n   • Nombres y apellidos\n   • Tipo de usuario\n   • Área de trabajo\n   • Fecha de ingreso\n   • Contraseña (mínimo 6 caracteres)\n3. Confirma tu contraseña\n4. Haz clic en "Registrar"\n\n¿Tienes alguna duda sobre algún campo?';
            }
        },
        {
            palabras: ['dni', 'documento', 'cedula', 'cédula', 'numero de documento'],
            respuesta: function () {
                return 'El DNI debe tener exactamente 8 dígitos numéricos.\n\n✅ Correcto: 12345678\n❌ Incorrecto: 1234567 (solo 7), 1234567A (tiene letra)\n\nSi el sistema rechaza tu DNI, verifica que tenga exactamente 8 números sin espacios ni letras.';
            }
        },
        {
            palabras: ['contraseña', 'clave', 'password', 'contrasena', 'pass'],
            respuesta: function () {
                return 'Requisitos de contraseña:\n\n• Mínimo 6 caracteres\n• Puede tener letras, números y símbolos\n• Debes confirmarla en el segundo campo\n• Ambas contraseñas deben ser iguales\n\nSi olvidas tu contraseña, contacta al Administrador del sistema.';
            }
        },
        {
            palabras: ['login', 'iniciar sesion', 'iniciar sesión', 'ingresar', 'entrar', 'acceder', 'como inicio'],
            respuesta: function () {
                return 'Para iniciar sesión:\n\n1. Ingresa tu DNI (8 dígitos)\n2. Ingresa tu contraseña\n3. Haz clic en "Ingresar"\n\nPosibles errores:\n• "DNI o contraseña incorrectos" → Verifica tus datos\n• "Usuario inactivo" → Contacta al Administrador\n• No tienes cuenta → Regístrate primero';
            }
        },
        {
            palabras: ['tipo', 'tipos de usuario', 'roles', 'rol', 'usuario', 'operario', 'supervisor', 'administrador', 'admin', 'diferencia'],
            respuesta: function () {
                return 'El sistema tiene 3 tipos de usuario:\n\n👷 Operario:\n• Registrar y ver sus solicitudes\n• Hacer check-in/check-out de maquinaria\n\n👔 Supervisor:\n• Gestionar solicitudes de operarios\n• Administrar inventario de maquinaria\n• Ver todas las actividades\n\n🔑 Administrador:\n• Acceso completo al sistema\n• Gestión de solicitudes y maquinaria\n• Reportes y configuración\n\n¿Quieres saber más sobre algún rol?';
            }
        },
        {
            palabras: ['solicitud', 'solicitudes', 'pedido', 'reporte', 'registrar solicitud', 'nueva solicitud'],
            respuesta: function () {
                return 'Sobre las solicitudes de trabajo:\n\n📝 Para crear una solicitud (solo Operarios):\n1. Ve a "Registrar Solicitud" en el menú\n2. Escribe la descripción del trabajo\n3. Selecciona el área y la prioridad\n4. Haz clic en Guardar\n\n📋 Estados de una solicitud:\n• Pendiente → Recién creada\n• En revisión → El supervisor la está revisando\n• Aprobado → Fue aceptada\n• Rechazado → Fue denegada\n\nLos supervisores y administradores gestionan las solicitudes desde "Gestión de Solicitudes".';
            }
        },
        {
            palabras: ['maquinaria', 'maquinas', 'máquinas', 'equipo', 'equipos', 'inventario'],
            respuesta: function () {
                return 'Sobre la gestión de maquinaria:\n\n🔧 Estados de maquinaria:\n• Operativo → Disponible para uso\n• En Mantenimiento → No disponible\n• Inactivo → Fuera de servicio\n\n📌 ¿Quién puede administrarla?\n• Supervisores y Administradores pueden registrar y actualizar maquinaria\n• Solo maquinaria "Operativa" aparece disponible para check-in\n\n⚠️ No se puede eliminar maquinaria con estado "Operativo".';
            }
        },
        {
            palabras: ['checkin', 'check-in', 'check in', 'checkout', 'check-out', 'check out', 'jornada', 'actividad', 'inicio jornada'],
            respuesta: function () {
                return 'Sobre la actividad de maquinaria:\n\n▶️ Check-In (iniciar jornada):\n1. Ve a "Actividad Maquinaria" → Check-In\n2. Selecciona la máquina (debe estar Operativa)\n3. Indica la zona de trabajo\n4. Registra el combustible inicial\n5. Estima las horas de trabajo\n6. Confirma para iniciar\n\n⏹️ Check-Out (finalizar jornada):\n1. Ingresa el combustible final\n2. Registra las horas reales trabajadas\n3. Si hubo retraso, explica el motivo\n4. Si la máquina se averió, usa el botón de avería\n\nSolo los Operarios pueden hacer check-in y check-out.';
            }
        },
        {
            palabras: ['averia', 'avería', 'falla', 'daño', 'dano', 'roto', 'averiado'],
            respuesta: function () {
                return 'Si una máquina se averió durante la jornada:\n\n1. En la pantalla de monitoreo activo, haz clic en "Reportar Avería"\n2. Describe la falla en el campo de observaciones\n3. Confirma el reporte\n\nLa máquina quedará en estado AVERIADO y logística será notificada. No podrás hacer nuevo check-in con esa máquina hasta que sea reparada y vuelva a estado Operativo.';
            }
        },
        {
            palabras: ['area', 'área', 'zona', 'departamento', 'campo', 'planta', 'logistica', 'logística'],
            respuesta: function () {
                return 'Las áreas de trabajo disponibles en el sistema son las configuradas para la empresa Pomalca (ej: Campo, Planta, Logística, Mantenimiento, etc.).\n\nDebes seleccionar tu área al momento del registro y también al crear solicitudes o iniciar jornadas de maquinaria.';
            }
        },
        {
            palabras: ['error', 'fallo', 'no funciona', 'problema', 'no puedo', 'no me deja'],
            respuesta: function () {
                return 'Problemas frecuentes y soluciones:\n\n❌ "DNI o contraseña incorrectos"\n→ Verifica que escribiste bien tu DNI (8 dígitos) y contraseña\n\n❌ "DNI debe tener 8 dígitos"\n→ Tu DNI tiene más o menos de 8 números\n\n❌ "Las contraseñas no coinciden"\n→ Escribe la misma contraseña en ambos campos\n\n❌ "No tienes permisos"\n→ Tu rol de usuario no tiene acceso a esa función\n\n❌ "DNI o correo ya registrados"\n→ Ya existe una cuenta con esos datos\n\nSi el problema persiste, contacta al Administrador.';
            }
        },
        {
            palabras: ['gracias', 'perfecto', 'ok', 'listo', 'entendi', 'entendí', 'claro', 'excelente', 'genial'],
            respuesta: function () {
                return '¡Con gusto! Si tienes más preguntas sobre el sistema, aquí estaré. ¿Hay algo más en lo que pueda ayudarte?';
            }
        },
        {
            palabras: ['adios', 'adiós', 'chao', 'hasta luego', 'bye'],
            respuesta: function () {
                return '¡Hasta luego! Si necesitas ayuda con el sistema, no dudes en consultarme. ¡Que tengas un buen día!';
            }
        }
    ];

    var RESPUESTA_DEFAULT = 'No encontré información específica sobre eso. Puedo ayudarte con estos temas:\n\n• Registro de usuario\n• Inicio de sesión\n• Tipos de usuario (Operario, Supervisor, Administrador)\n• Solicitudes de trabajo\n• Gestión de maquinaria\n• Check-in / Check-out de jornadas\n• Solución de errores\n\n¿Sobre cuál de estos temas tienes dudas?';

    var WELCOME_MSG = '¡Hola! Soy el asistente del Sistema de Gestión de Pomalca.\n\nEstoy aquí para orientarte sobre el registro, inicio de sesión y el uso del sistema. ¿En qué te puedo ayudar?';

    var QUICK_REPLIES = [
        '¿Cómo me registro?',
        '¿Cuáles son los tipos de usuario?',
        '¿Cómo registro una solicitud?',
        '¿Qué es el check-in de maquinaria?'
    ];

    // ================================================================
    // MOTOR DE RESPUESTAS
    // ================================================================

    function obtenerRespuesta(texto) {
        var normalizado = texto.toLowerCase()
            .normalize('NFD').replace(/[̀-ͯ]/g, '')
            .replace(/[^a-z0-9 ]/g, ' ');

        for (var i = 0; i < REGLAS.length; i++) {
            var regla = REGLAS[i];
            for (var j = 0; j < regla.palabras.length; j++) {
                if (normalizado.indexOf(regla.palabras[j]) !== -1) {
                    return regla.respuesta();
                }
            }
        }
        return RESPUESTA_DEFAULT;
    }

    // ================================================================
    // UI
    // ================================================================

    var isOpen = false;

    function buildWidget() {
        var btn = document.createElement('button');
        btn.id = 'chatbot-toggle';
        btn.title = 'Asistente Pomalca';
        btn.innerHTML = '<span>💬</span>';
        btn.addEventListener('click', toggleChat);

        var panel = document.createElement('div');
        panel.id = 'chatbot-panel';
        panel.setAttribute('aria-hidden', 'true');
        panel.innerHTML = [
            '<div class="chatbot-header">',
            '  <div class="chatbot-header-info">',
            '    <div class="chatbot-avatar">P</div>',
            '    <div>',
            '      <div class="chatbot-name">Asistente Pomalca</div>',
            '      <div class="chatbot-status">En línea</div>',
            '    </div>',
            '  </div>',
            '  <button class="chatbot-close" title="Cerrar">&times;</button>',
            '</div>',
            '<div class="chatbot-messages" id="chatbot-messages"></div>',
            '<div class="chatbot-quick-replies" id="chatbot-quick-replies"></div>',
            '<div class="chatbot-input-area">',
            '  <textarea id="chatbot-input" placeholder="Escribe tu pregunta..." rows="1" maxlength="300"></textarea>',
            '  <button id="chatbot-send" title="Enviar">&#9658;</button>',
            '</div>'
        ].join('');

        document.body.appendChild(btn);
        document.body.appendChild(panel);

        panel.querySelector('.chatbot-close').addEventListener('click', toggleChat);
        document.getElementById('chatbot-send').addEventListener('click', enviarMensaje);
        document.getElementById('chatbot-input').addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                enviarMensaje();
            }
        });

        renderQuickReplies();
        agregarMensaje('bot', WELCOME_MSG);
    }

    function renderQuickReplies() {
        var container = document.getElementById('chatbot-quick-replies');
        container.innerHTML = '';
        QUICK_REPLIES.forEach(function (texto) {
            var chip = document.createElement('button');
            chip.className = 'quick-reply-chip';
            chip.textContent = texto;
            chip.addEventListener('click', function () { procesarTexto(texto); });
            container.appendChild(chip);
        });
    }

    function toggleChat() {
        isOpen = !isOpen;
        var panel = document.getElementById('chatbot-panel');
        var btn = document.getElementById('chatbot-toggle');
        panel.classList.toggle('chatbot-open', isOpen);
        panel.setAttribute('aria-hidden', String(!isOpen));
        btn.classList.toggle('chatbot-active', isOpen);
        if (isOpen) {
            setTimeout(function () { document.getElementById('chatbot-input').focus(); }, 180);
        }
    }

    function agregarMensaje(rol, texto) {
        var container = document.getElementById('chatbot-messages');
        var wrapper = document.createElement('div');
        wrapper.className = 'chatbot-msg ' + (rol === 'bot' ? 'msg-bot' : 'msg-user');
        var bubble = document.createElement('div');
        bubble.className = 'chatbot-bubble';
        bubble.textContent = texto;
        wrapper.appendChild(bubble);
        container.appendChild(wrapper);
        container.scrollTop = container.scrollHeight;
    }

    function mostrarEscribiendo() {
        var container = document.getElementById('chatbot-messages');
        var wrapper = document.createElement('div');
        wrapper.className = 'chatbot-msg msg-bot';
        wrapper.id = 'chatbot-typing';
        wrapper.innerHTML = '<div class="chatbot-bubble typing-indicator"><span></span><span></span><span></span></div>';
        container.appendChild(wrapper);
        container.scrollTop = container.scrollHeight;
    }

    function quitarEscribiendo() {
        var el = document.getElementById('chatbot-typing');
        if (el) el.remove();
    }

    function enviarMensaje() {
        var input = document.getElementById('chatbot-input');
        var texto = input.value.trim();
        if (!texto) return;
        input.value = '';
        procesarTexto(texto);
    }

    function procesarTexto(texto) {
        document.getElementById('chatbot-quick-replies').style.display = 'none';
        agregarMensaje('user', texto);
        mostrarEscribiendo();

        // Simula un pequeño delay para que se sienta natural
        setTimeout(function () {
            quitarEscribiendo();
            var respuesta = obtenerRespuesta(texto);
            agregarMensaje('bot', respuesta);
        }, 500);
    }

    // ================================================================
    // INIT
    // ================================================================

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', buildWidget);
    } else {
        buildWidget();
    }

})();
