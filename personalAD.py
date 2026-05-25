from bd import obtener_conexion


class clsPersonal:
    def __init__(self, dni, nombres, apellidos, telefono, correo,
                 tipo_usuario, area, puesto, fecha_ingreso):
        self.dni           = dni
        self.nombres       = nombres
        self.apellidos     = apellidos
        self.telefono      = telefono
        self.correo        = correo
        self.tipo_usuario  = tipo_usuario
        self.area          = area
        self.puesto        = puesto
        self.fecha_ingreso = fecha_ingreso


def insertar_personal(personal):
    try:
        conn = obtener_conexion()

        if conn is None:
            return False

        with conn:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO personal
                    (dni, nombres, apellidos, telefono, correo,
                     tipo_usuario, area, puesto, fecha_ingreso)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    personal.fecha_ingreso
                ))

            conn.commit()

        return True

    except Exception as e:
        print("Error al insertar personal:", repr(e))
        return False