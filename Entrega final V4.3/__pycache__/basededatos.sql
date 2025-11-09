-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS NBA;

-- Usar la base de datos
USE NBA;

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100) NOT NULL UNIQUE,
    contraseña VARCHAR(100) NOT NULL,
    email VARCHAR(100)
);

-- Insertar usuarios de prueba
INSERT INTO usuarios (usuario, contraseña, email) VALUES 
('Hernan', '1234', 'hernan@ejemplo.com'),
('Alan', '1234', 'alan@ejemplo.com'),
('usuario1', 'password1', 'usuario1@ejemplo.com'),
('usuario2', 'password2', 'usuario2@ejemplo.com');

-- Verificar que se creó todo correctamente
SELECT '=== BASE DE DATOS CREADA EXITOSAMENTE ===' as Mensaje;

-- Mostrar las tablas
SHOW TABLES;

-- Mostrar los usuarios insertados
SELECT * FROM usuarios;