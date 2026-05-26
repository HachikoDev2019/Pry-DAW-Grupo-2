import pymysql.cursors
from bd import obtener_conexion

class clsActividad:
    def __init__(self, maquina, zona, combustible_inicial, horas_estimadas):
        self.maquina = maquina
        self.zona = zona
        self.combustible_inicial = combustible_inicial
        self.horas_estimadas = horas_estimadas
        self.estado = "EN RUTA"

def iniciar_actividad(actividad):
    try:
        conn = obtener_conexion()
        if conn is None: return None
        with conn:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO actividad_maquinaria 
                    (maquina, zona, combustible_inicial, horas_estimadas, estado) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    actividad.maquina, actividad.zona, 
                    actividad.combustible_inicial, actividad.horas_estimadas, actividad.estado
                ))
                id_generado = cursor.lastrowid
            conn.commit()
        return id_generado
    except Exception as e:
        print("Error al iniciar actividad:", repr(e))
        return None

def listar_actividades_activas():
    try:
        conn = obtener_conexion()
        if conn is None: return []
        with conn:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM actividad_maquinaria ORDER BY fecha_inicio DESC"
                cursor.execute(sql)
                return cursor.fetchall()
    except Exception as e:
        print("Error al listar actividades:", repr(e))
        return []

def obtener_actividad(id_actividad):
    try:
        conn = obtener_conexion()
        if conn is None: return None
        with conn:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM actividad_maquinaria WHERE id_actividad = %s"
                cursor.execute(sql, (id_actividad,))
                return cursor.fetchone()
    except Exception as e:
        print("Error al obtener actividad:", repr(e))
        return None

def finalizar_actividad(id_actividad, combustible_final, horas_reales, motivo_retraso, estado, observacion_falla):
    try:
        conn = obtener_conexion()
        if conn is None: return False
        with conn:
            with conn.cursor() as cursor:
                sql = """
                    UPDATE actividad_maquinaria 
                    SET estado = %s, combustible_final = %s, horas_reales = %s, 
                        motivo_retraso = %s, observacion_falla = %s, fecha_fin = CURRENT_TIMESTAMP
                    WHERE id_actividad = %s
                """
                cursor.execute(sql, (estado, combustible_final, horas_reales, motivo_retraso, observacion_falla, id_actividad))
            conn.commit()
        return True
    except Exception as e:
        print("Error al finalizar actividad:", repr(e))
        return False