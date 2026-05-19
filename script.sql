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