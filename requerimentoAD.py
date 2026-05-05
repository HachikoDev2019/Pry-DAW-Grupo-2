import pymysql.cursors

class clsRequerimiento:
    def __init__(self, p_titulo, p_area, p_fecha_limite, p_descripcion):
        self.titulo = p_titulo
        self.area = p_area
        self.fecha_limite = p_fecha_limite
        self.descripcion = p_descripcion

def obtenerconexion():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='db_pomalca',
            cursorclass=pymysql.cursors.DictCursor
        )
        if connection:
            return connection
        return None
    except Exception as e:
        print("Error de conexión: ", repr(e))
        return None
    
def insertar_requerimiento(p_Requerimiento):
    try:
        conn = obtenerconexion()
        if conn:
            with conn:
                with conn.cursor() as cursor:
                    # Se asume una tabla 'requerimientos' con estado 'Pendiente' por defecto
                    sql = """INSERT INTO requerimientos 
                             (titulo, area_solicitante, fecha_limite, descripcion, estado) 
                             VALUES (%s, %s, %s, %s, 'Pendiente')"""
                    
                    cursor.execute(sql, (
                        p_Requerimiento.titulo,
                        p_Requerimiento.area, 
                        p_Requerimiento.fecha_limite, 
                        p_Requerimiento.descripcion
                    ))
                conn.commit()
            return True
        return False
    except Exception as e:
        print("Error al insertar: ", repr(e))
        return False