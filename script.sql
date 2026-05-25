CREATE TABLE maquinaria (
    id_maquinaria INT AUTO_INCREMENT PRIMARY KEY,
    
    nombre_codigo VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    area VARCHAR(100),
    
    estado ENUM('Activo', 'Mantenimiento', 'Inactivo'),
    
    observaciones TEXT
);
CREATE TABLE IF NOT EXISTS solicitudes (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    trabajador VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    area VARCHAR(100) NOT NULL,
    prioridad ENUM('Alta', 'Media', 'Baja') NOT NULL,
    estado ENUM('Pendiente', 'En revisión', 'Aprobado', 'Rechazado') DEFAULT 'Pendiente',
    comentario TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);