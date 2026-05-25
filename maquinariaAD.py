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