
from bd import obtener_conexion
import pymysql.cursors
 
 
class clsPersonal:
    def __init__(self, dni, nombres, apellidos, telefono, correo,
                 tipo_usuario, area, puesto, fecha_ingreso, password):
        self.dni           = dni
        self.nombres       = nombres
        self.apellidos     = apellidos
        self.telefono      = telefono
        self.correo        = correo
        self.tipo_usuario  = tipo_usuario
        self.area          = area
        self.puesto        = puesto
        self.fecha_ingreso = fecha_ingreso
        self.password      = password
 
 
def insertar_personal(personal):
    try:
        conn = obtener_conexion()
 
        if conn is None:
            print("No se pudo conectar a la BD.")
            return False
 
        with conn:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO personal
                    (dni, nombres, apellidos, telefono, correo,
                     tipo_usuario, area, puesto, fecha_ingreso, password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    personal.dni,
                    personal.nombres,
                    personal.apellidos,
                    personal.telefono,
                    personal.correo,
                    personal.tipo_usuario,
                    personal.area,
                    personal.puesto,
                    personal.fecha_ingreso,
                    personal.password
                ))
            conn.commit()
 
        return True
 
    except Exception as e:
        print("Error al insertar personal:", repr(e))
        return False
 
 
def verificar_credenciales(dni, password):
    try:
        conexion = obtener_conexion()
 
        if conexion is None:
            print("No se pudo conectar con MySQL en verificar_credenciales.")
            return None
 
        dni_buscar      = str(dni).strip()
        password_buscar = str(password).strip()
 
        with conexion:
            with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
                query = """
                    SELECT id_personal, nombres, apellidos, tipo_usuario, password, estado
                    FROM personal
                    WHERE TRIM(dni) = %s
                """
                cursor.execute(query, (dni_buscar,))
                trabajador = cursor.fetchone()
 
                if trabajador:
                    db_password = str(trabajador['password']).strip()
                    db_estado   = str(trabajador['estado']).strip()
 
                    print(f"[DEBUG] DNI encontrado. Estado: {db_estado}")
                    print(f"[DEBUG] Pass BD: '{db_password}' | Pass ingresada: '{password_buscar}'")
 
                    if db_password == password_buscar:
                        if db_estado == 'Activo':
                            return {
                                'id_personal': trabajador['id_personal'],
                                'nombres':     trabajador['nombres'],
                                'apellidos':   trabajador['apellidos'],
                                'tipo_usuario':trabajador['tipo_usuario']
                            }
                        else:
                            print("[LOGIN] Usuario inactivo.")
                            return None
                    else:
                        print("[LOGIN] Contraseña incorrecta.")
                        return None
                else:
                    print(f"[LOGIN] No se encontró DNI: {dni_buscar}")
                    return None
 
    except Exception as err:
        print(f"Error crítico en verificar_credenciales: {err}")
        return None