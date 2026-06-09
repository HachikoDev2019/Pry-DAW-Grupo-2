let reqs = [];
let reqCounter = 41;

function nextCode() {
    reqCounter++;
    return 'REQ-' + String(reqCounter).padStart(4, '0');
}

function openModalReq() {
    const modal = document.getElementById('modalReq');

    if (!modal) return;

    document.getElementById('fCodigo').value = nextCode();
    document.getElementById('fFecha').value = new Date().toISOString().slice(0, 10);
    document.getElementById('fDesc').value = '';
    document.getElementById('fArea').value = '';
    document.getElementById('fPrio').value = '';
    document.getElementById('fSolic').value = '';
    document.getElementById('fEstado').value = '';
    document.getElementById('fObs').value = '';

    modal.classList.add('open');
}

function closeModalReq() {
    const modal = document.getElementById('modalReq');

    if (!modal) return;

    modal.classList.remove('open');
}

function saveReq() {
    const codigo = document.getElementById('fCodigo').value.trim();
    const desc = document.getElementById('fDesc').value.trim();
    const area = document.getElementById('fArea').value;
    const prio = document.getElementById('fPrio').value;
    const solic = document.getElementById('fSolic').value.trim();
    const fecha = document.getElementById('fFecha').value;
    const estado = document.getElementById('fEstado').value;

    if (!codigo || !desc || !area || !prio || !solic || !fecha || !estado) {
        notify('Complete todos los campos obligatorios', 'error');
        return;
    }

    reqs.unshift({
        codigo,
        desc,
        area,
        prio,
        solic,
        fecha,
        estado
    });

    closeModalReq();
    renderTable();
    updateStats();
    notify('Requerimiento registrado correctamente');
}

function renderTable() {
    const tbody = document.getElementById('reqBody');

    if (!tbody) return;

    tbody.innerHTML = '';

    if (reqs.length === 0) {
        tbody.innerHTML = `
            <tr class="empty-row">
                <td colspan="8">
                    No hay requerimientos registrados. Haga clic en "+ Nuevo Requerimiento" para comenzar.
                </td>
            </tr>
        `;
        return;
    }

    reqs.forEach((req, index) => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td><strong>${req.codigo}</strong></td>
            <td>${req.desc}</td>
            <td>${req.area}</td>
            <td>${req.prio}</td>
            <td>${req.solic}</td>
            <td>${req.fecha}</td>
            <td>${req.estado}</td>
            <td>
                <button class="btn-secondary" onclick="deleteReq(${index})">
                    Eliminar
                </button>
            </td>
        `;

        tbody.appendChild(row);
    });
}

function deleteReq(index) {
    reqs.splice(index, 1);
    renderTable();
    updateStats();
    notify('Requerimiento eliminado', 'error');
}

function updateStats() {
    const statAbiertos = document.getElementById('statAbiertos');

    if (!statAbiertos) return;

    const abiertos = reqs.filter(r => r.estado !== 'Aprobado' && r.estado !== 'Rechazado').length;
    const licitacion = reqs.filter(r => r.estado === 'En Licitación').length;
    const pendientes = reqs.filter(r => r.estado === 'Pendiente').length;
    const cerrados = reqs.filter(r => r.estado === 'Aprobado').length;
    const alta = reqs.filter(r => r.prio === 'Alta').length;

    document.getElementById('statAbiertos').textContent = abiertos;
    document.getElementById('statLicit').textContent = licitacion;
    document.getElementById('statPend').textContent = pendientes;
    document.getElementById('statCerrados').textContent = cerrados;
    document.getElementById('statAltaPrio').textContent = alta > 0 ? alta + ' alta prioridad' : 'sin alta prioridad';
    document.getElementById('statLicitSub').textContent = licitacion > 0 ? 'en proceso' : 'sin ofertas aún';
}

function notify(message, type = '') {
    const notif = document.getElementById('notif');

    if (!notif) return;

    notif.textContent = message;
    notif.className = 'notif' + (type ? ' ' + type : '');
    notif.classList.add('show');

    setTimeout(() => {
        notif.classList.remove('show');
    }, 2500);
}

document.addEventListener('click', function (event) {
    const modal = document.getElementById('modalReq');

    if (modal && event.target === modal) {
        closeModalReq();
    }
});