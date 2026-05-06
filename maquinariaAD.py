import pymysql.cursors

class clsMaquinaria:
    def __init__(self, p_nombre_codigo, p_tipo, p_marca, p_modelo, p_area, p_estado, p_observaciones):
        self.nombre_codigo = p_nombre_codigo
        self.tipo = p_tipo
        self.marca = p_marca
        self.modelo = p_modelo
        self.area = p_area
        self.estado = p_estado
        self.observaciones = p_observaciones

def obtenerconexion():
    try:
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='',
                                     database='db_pomalca',
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection
    except Exception as e:
        print("Error de conexión:", repr(e))
        return None
    
def insertar_maquinaria(p_Maquinaria):
    try:
        conn = obtenerconexion()
        if conn:
            with conn:
                with conn.cursor() as cursor:
                    sql = """INSERT INTO maquinaria 
                             (nombre_codigo, tipo, marca, modelo, area, estado, observaciones) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (
                        p_Maquinaria.nombre_codigo, p_Maquinaria.tipo, 
                        p_Maquinaria.marca, p_Maquinaria.modelo, 
                        p_Maquinaria.area, p_Maquinaria.estado, 
                        p_Maquinaria.observaciones
                    ))
                conn.commit()
            return True
        return False
    except Exception as e:
        print("Error al insertar:", repr(e))
        return False
