CREATE DATABASE IF NOT EXISTS db_pomalca
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

USE db_pomalca;

CREATE TABLE IF NOT EXISTS maquinaria (
    id_maquinaria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_codigo VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    area VARCHAR(100),
    estado ENUM('Operativo', 'En Mantenimiento', 'Inactivo') NOT NULL,
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS personal (
    id_personal INT AUTO_INCREMENT PRIMARY KEY,
    dni CHAR(8) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    telefono VARCHAR(15),
    correo VARCHAR(100),
    password VARCHAR(255) NOT NULL, -- Nueva columna agregada
    tipo_usuario ENUM('Administrador', 'Trabajador') NOT NULL DEFAULT 'Trabajador',
    area VARCHAR(100) NOT NULL,
    puesto VARCHAR(100) NOT NULL,
    fecha_ingreso DATE NOT NULL,
    estado ENUM('Activo', 'Inactivo') NOT NULL DEFAULT 'Activo',
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



INSERT INTO personal (
    dni,
    nombres,
    apellidos,
    telefono,
    correo,
    password,
    tipo_usuario,
    area,
    puesto,
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
    'Administrador',
    '2026-05-26',
    'Activo',
    'Acceso principal'
);

CREATE TABLE IF NOT EXISTS actividad_maquinaria (
    id_actividad INT AUTO_INCREMENT PRIMARY KEY,
    maquina VARCHAR(100) NOT NULL,
    zona VARCHAR(100) NOT NULL,
    combustible_inicial ENUM('100%', '75%', '50%', '25%') NOT NULL,
    horas_estimadas INT NOT NULL,
    estado ENUM('EN RUTA', 'FINALIZADO', 'AVERIADO') DEFAULT 'EN RUTA',
    combustible_final ENUM('100%', '75%', '50%', '25%', 'Reserva'),
    horas_reales INT,
    motivo_retraso TEXT,
    observacion_falla TEXT,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP NULL DEFAULT NULL
);