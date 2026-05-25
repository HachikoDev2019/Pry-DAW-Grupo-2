import pymysql.cursors


def obtener_conexion():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="db_pomalca",
            cursorclass=pymysql.cursors.DictCursor
        )

        return connection

    except Exception as e:
        print("Error de conexión:", repr(e))
        return None