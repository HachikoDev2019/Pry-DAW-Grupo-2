import pymysql.cursors
from bd import obtener_conexion

class clsMaquinaria:
    def __init__(self, nombre_codigo, tipo, marca, modelo, area, estado, observaciones):
        
        self.nombre_codigo = nombre_codigo
        self.tipo = tipo
        self.marca = marca
        self.modelo = modelo
        self.area = area
        self.estado = estado
        self.observaciones = observaciones

def insertar_maquinaria(maquinaria):
    try:
        conn = obtener_conexion()

        if conn is None:
            return False

        with conn:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO maquinaria
                    (nombre_codigo, tipo, marca, modelo, area, estado, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                cursor.execute(sql, (
                    maquinaria.nombre_codigo,
                    maquinaria.tipo,
                    maquinaria.marca,
                    maquinaria.modelo,
                    maquinaria.area,
                    maquinaria.estado,
                    maquinaria.observaciones
                ))

            conn.commit()

        return True

    except Exception as e:
        print("Error al insertar maquinaria:", repr(e))
        return False



def listar_maquinarias():
    """Trae el listado completo de maquinarias ordenadas por fecha de registro."""
    try:
        conn = obtener_conexion()
        if conn is None:
            return []  # Corregido de False a [] para mantener consistencia con los retornos
        with conn:
            with conn.cursor() as cursor:
                sql = """
                    SELECT id_maquinaria, nombre_codigo, tipo, marca, modelo, area, estado, observaciones, fecha_registro
                    FROM maquinaria
                    ORDER BY fecha_registro DESC
                """
                cursor.execute(sql)
                return cursor.fetchall()


    except Exception as e:
        print("Error al listar maquinarias:", repr(e))
        return []


def leer_maquinaria_xId(p_idMaquinaria):
    try:
        conn = obtener_conexion()
        result = None
        if conn:
            with conn:
                with conn.cursor() as cursor:
                    sql = "SELECT id_maquinaria, nombre_codigo, tipo, marca, modelo, area, estado, observaciones, fecha_registro FROM maquinaria WHERE id_maquinaria = %s"
                    cursor.execute(sql, (p_idMaquinaria,))
                    result = cursor.fetchall()  # O cursor.fetchone() según cómo manejes tu diccionario
        return result
    except Exception as e:
        raise



def listar_maquinarias_filtradas(estado=None, area=None, tipo=None):
    """Permite buscar maquinarias aplicando filtros dinámicos por estado, área o tipo."""
    try:
        conn = obtener_conexion()
        if conn is None:
            return []
        with conn:
            with conn.cursor() as cursor:
                # El truco del WHERE 1 = 1 nos permite concatenar ANDs de forma limpia
                sql = """
                    SELECT id_maquinaria, nombre_codigo, tipo, marca, modelo, area, estado, observaciones, fecha_registro
                    FROM maquinaria
                    WHERE 1 = 1
                """
                params = []
                
                if estado:
                    sql += " AND estado = %s"
                    params.append(estado)
                if area:
                    sql += " AND area = %s"
                    params.append(area)
                if tipo:
                    sql += " AND tipo = %s"
                    params.append(tipo)
                    
                sql += " ORDER BY fecha_registro DESC"
                
                cursor.execute(sql, params)
                return cursor.fetchall()
                
    except Exception as e:
        print("Error al filtrar maquinarias:", repr(e))
        return []
    

def actualizar_maquinaria(id_maquinaria, estado):
    try:
        conn = obtener_conexion()

        if conn is None:
            return False

        with conn:
            with conn.cursor() as cursor:

                sql = """
                    UPDATE maquinaria
                    SET estado = %s
                    WHERE id_maquinaria = %s
                """

                cursor.execute(sql, (estado, id_maquinaria))

            conn.commit()

        return True

    except Exception as e:
        print("Error al actualizar maquinaria:", repr(e))
        return False
    



def eliminar_maquinaria(id_maquinaria):
    try:
        conn = obtener_conexion()

        if conn is None:
            return False

        with conn:
            with conn.cursor() as cursor:

                sql = """
                DELETE FROM maquinaria
                WHERE id_maquinaria = %s
                """

                cursor.execute(sql, (id_maquinaria,))

            conn.commit()

        return True

    except Exception as e:
        print("Error al eliminar maquinaria:", repr(e))
        return False



def obtener_maquinaria(id_maquinaria):
    try:
        conn = obtener_conexion()

        if conn is None:
            return None

        with conn:
            with conn.cursor() as cursor:

                sql = """
                SELECT *
                FROM maquinaria
                WHERE id_maquinaria = %s
                """

                cursor.execute(sql, (id_maquinaria,))
                return cursor.fetchone()

    except Exception as e:
        print("Error:", repr(e))
        return None