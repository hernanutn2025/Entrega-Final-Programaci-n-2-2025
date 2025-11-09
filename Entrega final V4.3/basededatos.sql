CREATE DATABASE IF NOT EXISTS NBA;

USE NBA;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100) NOT NULL UNIQUE,
    contraseña VARCHAR(100) NOT NULL,
    email VARCHAR(100)
);

insert into Usuarios(usuario,contraseña,email) values("Hernan","1234","correo1");
insert into Usuarios(usuario,contraseña,email) values("Alan","1234","correo2");

SHOW TABLES;


