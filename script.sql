CREATE DATABASE IF NOT EXISTS db_pomalca
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

USE db_pomalca;

-- =========================================================
-- TABLA MAQUINARIA
-- =========================================================

CREATE TABLE IF NOT EXISTS maquinaria (
    id_maquinaria INT AUTO_INCREMENT PRIMARY KEY,
    
    nombre_codigo VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    area VARCHAR(100),

    estado ENUM(
        'Operativo',
        'En Mantenimiento',
        'Inactivo'
    ) NOT NULL,

    observaciones TEXT,

    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- TABLA PERSONAL
-- =========================================================

CREATE TABLE IF NOT EXISTS personal (
    id_personal INT AUTO_INCREMENT PRIMARY KEY,

    dni CHAR(8) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,

    telefono VARCHAR(15),
    correo VARCHAR(100),

    password VARCHAR(255) NOT NULL,

    tipo_usuario ENUM(
        'Operario',
        'Supervisor',
        'Administrador'
    ) NOT NULL DEFAULT 'Operario',

    area VARCHAR(100) NOT NULL,

    fecha_ingreso DATE NOT NULL,

    estado ENUM(
        'Activo',
        'Inactivo'
    ) NOT NULL DEFAULT 'Activo',

);

-- =========================================================
-- TABLA SOLICITUDES
-- =========================================================

CREATE TABLE IF NOT EXISTS solicitudes (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY,

    trabajador VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    area VARCHAR(100) NOT NULL,

    prioridad ENUM(
        'Alta',
        'Media',
        'Baja'
    ) NOT NULL,

    estado ENUM(
        'Pendiente',
        'En revisión',
        'Aprobado',
        'Rechazado'
    ) DEFAULT 'Pendiente',

    comentario TEXT,

    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- TABLA ACTIVIDAD MAQUINARIA
-- =========================================================

CREATE TABLE IF NOT EXISTS actividad_maquinaria (
    id_actividad INT AUTO_INCREMENT PRIMARY KEY,

    maquina VARCHAR(100) NOT NULL,
    zona VARCHAR(100) NOT NULL,

    combustible_inicial DECIMAL(10,2) NOT NULL,
    combustible_final DECIMAL(10,2),

    horas_estimadas DECIMAL(10,2) NOT NULL,
    horas_reales DECIMAL(10,2),

    motivo_retraso TEXT,
    observacion_falla TEXT,

    estado ENUM(
        'ACTIVO',
        'FINALIZADO',
        'AVERIADO'
    ) DEFAULT 'ACTIVO',

    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP NULL
);

-- =========================================================
-- ADMINISTRADOR
-- =========================================================

INSERT INTO personal (
    dni,
    nombres,
    apellidos,
    telefono,
    correo,
    password,
    tipo_usuario,
    area,
    fecha_ingreso,
    estado,
    observaciones
)
VALUES (
    '12345678',
    'Admin',
    'Principal',
    '999999999',
    'admin@gmail.com',
    '1234',
    'Administrador',
    'Sistemas',
    CURDATE(),
    'Activo',
    'Acceso principal'
);

-- =========================================================
-- TRABAJADORES DE PRUEBA
-- =========================================================

INSERT INTO personal (
    dni,
    nombres,
    apellidos,
    telefono,
    correo,
    password,
    tipo_usuario,
    area,
    fecha_ingreso,
    estado,
    observaciones
)
VALUES

(
    '11111111',
    'Carlos',
    'Ramirez',
    '911111111',
    'carlos.ramirez@gmail.com',
    '123456',
    'Operario',
    'Campo',
    CURDATE(),
    'Activo',
    'Operario de prueba'
),

(
    '22222222',
    'Maria',
    'Torres',
    '922222222',
    'maria.torres@gmail.com',
    '123456',
    'Operario',
    'Fábrica',
    CURDATE(),
    'Activo',
    'Operaria de prueba'
),

(
    '33333333',
    'Luis',
    'Fernandez',
    '933333333',
    'luis.fernandez@gmail.com',
    '123456',
    'Operario',
    'Mantenimiento',
    CURDATE(),
    'Activo',
    'Operario de prueba'
);

-- =========================================================
-- MAQUINARIA DE PRUEBA
-- =========================================================

INSERT INTO maquinaria (
    nombre_codigo,
    tipo,
    marca,
    modelo,
    area,
    estado,
    observaciones
)
VALUES

(
    'TR-001',
    'Tractor',
    'John Deere',
    '5075E',
    'Campo',
    'Operativo',
    'Asignado a cosecha norte'
),

(
    'CAL-003',
    'Caldera',
    'Bosch',
    'B300',
    'Fábrica',
    'En Mantenimiento',
    'Cambio de válvula principal'
),

(
    'COS-002',
    'Cosechadora',
    'Case IH',
    'A400',
    'Campo',
    'Operativo',
    'Operativa para turno noche'
);

-- =========================================================
-- SOLICITUDES DE PRUEBA
-- =========================================================

INSERT INTO solicitudes (
    trabajador,
    descripcion,
    area,
    prioridad,
    estado,
    comentario
)
VALUES

(
    'Carlos Ramirez',
    'Solicitud de repuestos para tractor TR-001',
    'Campo',
    'Alta',
    'Pendiente',
    NULL
),

(
    'Maria Torres',
    'Compra de implementos de seguridad industrial',
    'Fábrica',
    'Media',
    'En revisión',
    'Validando presupuesto'
),

(
    'Luis Fernandez',
    'Mantenimiento preventivo de caldera CAL-003',
    'Mantenimiento',
    'Alta',
    'Aprobado',
    'Programado para mañana'
);