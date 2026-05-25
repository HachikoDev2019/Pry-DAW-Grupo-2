import pymysql.cursors
from bd import obtener_conexion


class clsSolicitud:
    def __init__(self, trabajador, descripcion, area, prioridad):
        self.trabajador = trabajador
        self.descripcion = descripcion
        self.area = area
        self.prioridad = prioridad


def insertar_solicitud(solicitud):
    try:
        conn = obtener_conexion()

        with conn:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO solicitudes
                    (trabajador, descripcion, area, prioridad)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    solicitud.trabajador,
                    solicitud.descripcion,
                    solicitud.area,
                    solicitud.prioridad
                ))

            conn.commit()

        return True

    except Exception as e:
        print("Error al insertar solicitud:", repr(e))
        return False


def listar_mis_solicitudes(trabajador):
    try:
        conn = obtener_conexion()

        with conn:
            with conn.cursor() as cursor:
                sql = """
                    SELECT *
                    FROM solicitudes
                    WHERE trabajador = %s
                    ORDER BY fecha_registro DESC
                """
                cursor.execute(sql, (trabajador,))
                return cursor.fetchall()

    except Exception as e:
        print("Error al listar solicitudes:", repr(e))
        return []