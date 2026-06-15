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
            return None
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
                id_solicitud = cursor.lastrowid
            conn.commit()
        return id_solicitud
    except Exception as e:
        print("Error al insertar solicitud:", repr(e))
        return None


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
                sql = "SELECT * FROM solicitudes WHERE 1 = 1"
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


def eliminar_solicitud(id_solicitud):
    try:
        conn = obtener_conexion()
        if conn is None:
            return False
        with conn:
            with conn.cursor() as cursor:
                sql = "DELETE FROM solicitudes WHERE id_solicitud = %s"
                cursor.execute(sql, (id_solicitud,))
            conn.commit()
        return True
    except Exception as e:
        print("Error al eliminar solicitud:", repr(e))
        return False


def actualizar_solicitud_operario(id_solicitud, descripcion, area, prioridad):
    """Actualiza solo los campos que el operario puede editar (NO estado)"""
    try:
        conn = obtener_conexion()
        if conn is None:
            return False
        with conn:
            with conn.cursor() as cursor:
                sql = """
                    UPDATE solicitudes
                    SET descripcion = %s,
                        area = %s,
                        prioridad = %s
                    WHERE id_solicitud = %s
                """
                cursor.execute(sql, (descripcion, area, prioridad, id_solicitud))
            conn.commit()
        return True
    except Exception as e:
        print("Error al actualizar solicitud:", repr(e))
        return False


def actualizar_ruta_pdf(id_solicitud, ruta_pdf):
    """Guarda la ruta del PDF generado automáticamente al aprobar"""
    try:
        conn = obtener_conexion()
        if conn is None:
            return False
        with conn:
            with conn.cursor() as cursor:
                sql = """
                    UPDATE solicitudes
                    SET ruta_pdf = %s
                    WHERE id_solicitud = %s
                """
                cursor.execute(sql, (ruta_pdf, id_solicitud))
            conn.commit()
        return True
    except Exception as e:
        print("Error al guardar ruta PDF:", repr(e))
        return False


# =========================================================
# NUEVA FUNCIÓN — guarda el PDF firmado subido por el supervisor
# =========================================================

def actualizar_ruta_pdf_firmado(id_solicitud, ruta_pdf_firmado):
    """Guarda la ruta del PDF firmado con Certezia subido por el supervisor"""
    try:
        conn = obtener_conexion()
        if conn is None:
            return False
        with conn:
            with conn.cursor() as cursor:
                sql = """
                    UPDATE solicitudes
                    SET ruta_pdf_firmado = %s
                    WHERE id_solicitud = %s
                """
                cursor.execute(sql, (ruta_pdf_firmado, id_solicitud))
            conn.commit()
        return True
    except Exception as e:
        print("Error al guardar ruta PDF firmado:", repr(e))
        return False