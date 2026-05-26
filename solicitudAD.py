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
        if conn is None:
            return False
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
        if conn is None:
            return []
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
    
def listar_todas_solicitudes(estado=None, area=None, prioridad=None):
    try:
        conn = obtener_conexion()
        if conn is None:
            return []
        with conn:
            with conn.cursor() as cursor:
                sql = """
                    SELECT *
                    FROM solicitudes
                    WHERE 1 = 1
                """
                params = []
                if estado:
                    sql += " AND estado = %s"
                    params.append(estado)
                if area:
                    sql += " AND area = %s"
                    params.append(area)
                if prioridad:
                    sql += " AND prioridad = %s"
                    params.append(prioridad)
                sql += " ORDER BY fecha_registro DESC"
                cursor.execute(sql, params)
                return cursor.fetchall()
    except Exception as e:
        print("Error al listar todas las solicitudes:", repr(e))
        return []


def actualizar_solicitud(id_solicitud, estado, comentario):
    try:
        conn = obtener_conexion()
        if conn is None:
            return False
        with conn:
            with conn.cursor() as cursor:
                sql = """
                    UPDATE solicitudes
                    SET estado = %s,
                        comentario = %s
                    WHERE id_solicitud = %s
                """
                cursor.execute(sql, (estado, comentario, id_solicitud))
            conn.commit()
        return True
    except Exception as e:
        print("Error al actualizar solicitud:", repr(e))
        return False