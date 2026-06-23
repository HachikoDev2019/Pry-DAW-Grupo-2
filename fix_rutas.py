from bd import obtener_conexion

conn = obtener_conexion()
with conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT id_solicitud, ruta_pdf FROM solicitudes WHERE ruta_pdf IS NOT NULL")
        rows = cursor.fetchall()
        for r in rows:
            nueva = r["ruta_pdf"].replace("\\", "/")
            print(f'ID {r["id_solicitud"]}: {r["ruta_pdf"]!r} -> {nueva!r}')
            cursor.execute("UPDATE solicitudes SET ruta_pdf = %s WHERE id_solicitud = %s", (nueva, r["id_solicitud"]))
    conn.commit()
print("Rutas actualizadas correctamente.")
