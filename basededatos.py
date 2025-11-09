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

def guardar_partido(conexion, equipo_local, equipo_visitante, marcador_local, 
                   marcador_visitante, faltas_local, faltas_visitante, 
                   tiempo_muertos_local, tiempo_muertos_visitante, 
                   duracion_partido, usuario_registro,
                   puntos_q1_local=0, puntos_q2_local=0, puntos_q3_local=0, 
                   puntos_q4_local=0, puntos_te_local=0,
                   puntos_q1_visitante=0, puntos_q2_visitante=0, 
                   puntos_q3_visitante=0, puntos_q4_visitante=0, 
                   puntos_te_visitante=0, cuarto_actual=""):
    
    try:
        cursor = conexion.cursor()
        
        insertar_sql = """
        INSERT INTO partidos 
        (equipo_local, equipo_visitante, marcador_local, marcador_visitante,
         faltas_local, faltas_visitante, tiempo_muertos_local, tiempo_muertos_visitante,
         duracion_partido, usuario_registro,
         puntos_q1_local, puntos_q2_local, puntos_q3_local, puntos_q4_local, puntos_te_local,
         puntos_q1_visitante, puntos_q2_visitante, puntos_q3_visitante, puntos_q4_visitante, puntos_te_visitante,
         cuarto_actual) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        datos_partido = (equipo_local, equipo_visitante, marcador_local, marcador_visitante,
                        faltas_local, faltas_visitante, tiempo_muertos_local, 
                        tiempo_muertos_visitante, duracion_partido, usuario_registro,
                        puntos_q1_local, puntos_q2_local, puntos_q3_local, puntos_q4_local, puntos_te_local,
                        puntos_q1_visitante, puntos_q2_visitante, puntos_q3_visitante, puntos_q4_visitante, puntos_te_visitante,
                        cuarto_actual)
        
        cursor.execute(insertar_sql, datos_partido)
        conexion.commit()
        
        print(f"Partido guardado correctamente (ID: {cursor.lastrowid})")
        cursor.close()
        return cursor.lastrowid
        
    except Error as e:
        print(f"Error al guardar partido: {e}")
        return None

def obtener_partidos_usuario(conexion, usuario=None, limite=50):
    try:
        cursor = conexion.cursor(dictionary=True)
        
        if usuario:
            consulta = """
            SELECT * FROM partidos 
            WHERE usuario_registro = %s 
            ORDER BY fecha_partido DESC 
            LIMIT %s
            """
            cursor.execute(consulta, (usuario, limite))
        else:
            consulta = "SELECT * FROM partidos ORDER BY fecha_partido DESC LIMIT %s"
            cursor.execute(consulta, (limite,))
        
        partidos = cursor.fetchall()
        cursor.close()
        return partidos
        
    except Error as e:
        print(f"Error al obtener partidos: {e}")
        return []

def obtener_partido_por_id(conexion, id_partido):
    try:
        cursor = conexion.cursor(dictionary=True)
        
        consulta = "SELECT * FROM partidos WHERE id_partido = %s"
        cursor.execute(consulta, (id_partido,))
        
        partido = cursor.fetchone()
        cursor.close()
        return partido
        
    except Error as e:
        print(f"Error al obtener partido: {e}")
        return None

def obtener_historial_partidos(conexion, usuario=None):
    try:
        cursor = conexion.cursor(dictionary=True)
        
        if usuario:
            consulta = "SELECT * FROM partidos WHERE usuario_registro = %s ORDER BY fecha_partido DESC"
            cursor.execute(consulta, (usuario,))
        else:
            consulta = "SELECT * FROM partidos ORDER BY fecha_partido DESC"
            cursor.execute(consulta)
        
        partidos = cursor.fetchall()
        cursor.close()
        return partidos
        
    except Error as e:
        print(f"Error al obtener historial de partidos: {e}")
        return []

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