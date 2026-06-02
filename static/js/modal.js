/**
 * Sistema de modal de confirmación reutilizable
 * Uso: openModal({title, message, onConfirm, onCancel})
 */

let confirmCallback = null;
let cancelCallback = null;

// Función auxiliar para obtener elementos con validación
function getModalElements() {
    return {
        modalElement: document.getElementById('confirmModal'),
        modalTitle: document.getElementById('modalTitle'),
        modalMessage: document.getElementById('modalMessage'),
        modalConfirmBtn: document.getElementById('modalConfirm'),
        modalCancelBtn: document.getElementById('modalCancel')
    };
}

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

    const { modalElement, modalTitle, modalMessage } = getModalElements();
    
    if (!modalElement) {
        console.error('Modal element not found in DOM');
        return;
    }

    modalTitle.textContent = title;
    modalMessage.textContent = message;
    confirmCallback = onConfirm;
    cancelCallback = onCancel;

    // Usar clase en lugar de inline style
    modalElement.classList.add('show');
}

/**
 * Cierra el modal
 */
function closeModal() {
    const { modalElement } = getModalElements();
    
    if (!modalElement) return;
    
    // Remover clase en lugar de cambiar inline style
    modalElement.classList.remove('show');
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

/**
 * Función para confirmar logout
 */
function confirmLogout() {
    openModal({
        title: 'Cerrar Sesión',
        message: '¿Estás seguro que deseas cerrar sesión?',
        onConfirm: () => {
            const logoutForm = document.getElementById('logoutForm');
            if (logoutForm) {
                logoutForm.submit();
            }
        }
    });
}

// Inicializar event listeners cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const { modalElement, modalConfirmBtn, modalCancelBtn } = getModalElements();
    
    if (!modalElement) {
        console.error('confirmModal element not found in HTML');
        return;
    }

    // Event listeners
    if (modalConfirmBtn) {
        modalConfirmBtn.addEventListener('click', () => {
            if (confirmCallback) confirmCallback();
            closeModal();
        });
    }

    if (modalCancelBtn) {
        modalCancelBtn.addEventListener('click', () => {
            if (cancelCallback) cancelCallback();
            closeModal();
        });
    }

    // Cerrar modal con tecla Escape
    document.addEventListener('keydown', (e) => {
        const { modalElement } = getModalElements();
        if (e.key === 'Escape' && modalElement && modalElement.classList.contains('show')) {
            closeModal();
        }
    });

    // Cerrar modal al hacer clic en el overlay
    document.addEventListener('click', (e) => {
        const { modalElement } = getModalElements();
        if (modalElement && e.target === modalElement) {
            closeModal();
        }
    });
});
