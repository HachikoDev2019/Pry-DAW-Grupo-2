/**
 * Sistema de modal de confirmación reutilizable
 * Uso: confirmAction({title, message, onConfirm, onCancel})
 */

const modalElement = document.getElementById('confirmModal');
const modalTitle = document.getElementById('modalTitle');
const modalMessage = document.getElementById('modalMessage');
const modalConfirmBtn = document.getElementById('modalConfirm');
const modalCancelBtn = document.getElementById('modalCancel');

let confirmCallback = null;
let cancelCallback = null;

/**
 * Abre el modal con título y mensaje personalizados
 * @param {Object} options - Configuración del modal
 * @param {string} options.title - Título del modal
 * @param {string} options.message - Mensaje a mostrar
 * @param {Function} options.onConfirm - Callback al confirmar
 * @param {Function} options.onCancel - Callback al cancelar (opcional)
 */
function openModal(options = {}) {
    const {
        title = 'Confirmar',
        message = '¿Estás seguro?',
        onConfirm = null,
        onCancel = null
    } = options;

    modalTitle.textContent = title;
    modalMessage.textContent = message;
    confirmCallback = onConfirm;
    cancelCallback = onCancel;

    modalElement.style.display = 'flex';
}

/**
 * Cierra el modal
 */
function closeModal() {
    modalElement.style.display = 'none';
    confirmCallback = null;
    cancelCallback = null;
}

/**
 * Útil para formularios: previene submit y abre el modal
 * @param {HTMLFormElement} form - El formulario a proteger
 * @param {Object} options - Opciones del modal
 */
function confirmFormSubmit(form, options = {}) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const defaultOptions = {
            title: options.title || 'Confirmar registro',
            message: options.message || '¿Estás seguro que deseas continuar?',
            onConfirm: () => form.submit(),
            onCancel: () => closeModal()
        };

        openModal(defaultOptions);
    });
}

// Event listeners
modalConfirmBtn.addEventListener('click', () => {
    if (confirmCallback) confirmCallback();
    closeModal();
});

modalCancelBtn.addEventListener('click', () => {
    if (cancelCallback) cancelCallback();
    closeModal();
});

// Cerrar modal con tecla Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalElement.style.display === 'flex') {
        closeModal();
    }
});

// Cerrar modal al hacer clic en el overlay
document.addEventListener('click', (e) => {
    if (e.target === modalElement) {
        closeModal();
    }
});
