import mysql.connector
from mysql.connector import Error

def conectar_base():
    try:
        conexion=mysql.connector.connect(
            host="localhost",
            user="root",
            password="BASEDEDATOS-1",
            database="NBA"
        )
        if conexion.is_connected():
            print("Conexion exitosa a MySQL")
        return conexion
    except Error as e:
        print(f"Error al conectar a MySQL:{e}")
        return None
    
def registrar_usuario(conexion, usuario, contraseña, email):
    
    if verificar_usuario(conexion,usuario):
        print(f"Error: El usuario {usuario} ya existe.")
        return False
    else:    
        try:
            cursor = conexion.cursor()
            
            insertar_sql = "INSERT INTO usuarios (usuario, contraseña, email) VALUES (%s, %s, %s)"
            datos_usuario = (usuario, contraseña, email)
            
            cursor.execute(insertar_sql, datos_usuario)
            conexion.commit()
            
            print(f"Usuario '{usuario}' Registrado correctamente (ID: {cursor.lastrowid})")
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error al insertar usuario: {e}")
            return False

def verificar_usuario(conexion,usuario):
    try:
        cursor = conexion.cursor(buffered=True)
        consulta = "SELECT COUNT(*) FROM Usuarios where usuario = %s"
        cursor.execute(consulta,(usuario,))
        resultado = cursor.fetchone()[0]
        cursor.close()
        return resultado > 0
    
    except Error as e:
        print(f"Error al verificar el usuario{e}")
        return False 

def autenticar_usuario(conexion, usuario, contraseña):
    try:
        cursor = conexion.cursor(buffered=True)
        consulta = "SELECT contraseña FROM usuarios WHERE usuario = %s"
        
        cursor.execute(consulta, (usuario,))
        resultado = cursor.fetchone()
        cursor.close()

        if resultado:
            contraseña_almacenada = resultado[0]
            if contraseña_almacenada == contraseña: 
                return True
            else:
                return False
        else:
            return False

    except Error as e:
        print(f"Error al autenticar usuario: {e}")
        return False