from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

from maquinariaAD import clsMaquinaria, insertar_maquinaria, listar_maquinarias, actualizar_maquinaria, eliminar_maquinaria, obtener_maquinaria

from solicitudAD import (
    clsSolicitud,
    insertar_solicitud,
    listar_mis_solicitudes,
    listar_todas_solicitudes,
    actualizar_solicitud
)

from personalAD import (
    clsPersonal,
    insertar_personal,
    verificar_credenciales,
    listar_personal,
    leer_personal_xDNI
)

from actividadAD import (
    clsActividad,
    iniciar_actividad,
    listar_actividades_activas,
    obtener_actividad,
    finalizar_actividad
)


app = Flask(__name__)
app.secret_key = "pomalca_secret_key"


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def usuario_logueado():
    return "id_personal" in session


def es_administrador():
    return session.get("tipo_usuario") == "Administrador"


def es_supervisor():
    return session.get("tipo_usuario") == "Supervisor"


def es_operario():
    return session.get("tipo_usuario") == "Operario"


def es_supervisor_o_admin():
    return session.get("tipo_usuario") in ("Supervisor", "Administrador")


def nombre_usuario_actual():
    return f"{session.get('nombres', '')} {session.get('apellidos', '')}".strip()


# =========================================================
# LOGIN / LOGOUT
# =========================================================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        dni_ingresado = request.form.get("dni", "").strip()
        password_ingresada = request.form.get("password", "").strip()

        trabajador = verificar_credenciales(dni_ingresado, password_ingresada)

        if trabajador:
            session["id_personal"] = trabajador["id_personal"]
            session["nombres"] = trabajador["nombres"]
            session["apellidos"] = trabajador["apellidos"]
            session["tipo_usuario"] = trabajador["tipo_usuario"]

            flash(f"¡Bienvenido, {trabajador['nombres']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Número de DNI o contraseña incorrectos, o usuario inactivo.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("login"))


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():
    if not usuario_logueado():
        flash("Por favor, inicie sesión para acceder al portal.", "error")
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# =========================================================
# REGISTRO DE PERSONAL
# =========================================================

@app.route("/registro")
def registro():
    return render_template("registro.html")


@app.route("/registro_persona")
def registropersona():
    return redirect(url_for("registro"))


@app.route("/guardar_personal", methods=["POST"])
def guardar_personal():
    dni = request.form.get("dni", "").strip()
    nombres = request.form.get("nombres", "").strip()
    apellidos = request.form.get("apellidos", "").strip()
    telefono = request.form.get("telefono", "").strip()
    correo = request.form.get("correo", "").strip()
    tipo_usuario = request.form.get("tipo_usuario", "").strip()
    area = request.form.get("area", "").strip()
    fecha_ingreso = request.form.get("fecha_ingreso", "").strip()
    password = request.form.get("password", "")
    password2 = request.form.get("password2", "")

    if not all([dni, nombres, apellidos, tipo_usuario, area, fecha_ingreso, password]):
        flash("Completa todos los campos obligatorios.", "error")
        return redirect(url_for("registro"))

    if len(dni) != 8 or not dni.isdigit():
        flash("El DNI debe tener exactamente 8 dígitos.", "error")
        return redirect(url_for("registro"))

    if len(password) < 6:
        flash("La contraseña debe tener al menos 6 caracteres.", "error")
        return redirect(url_for("registro"))

    if password != password2:
        flash("Las contraseñas no coinciden.", "error")
        return redirect(url_for("registro"))

    try:
        personal = clsPersonal(
            dni,
            nombres,
            apellidos,
            telefono,
            correo,
            tipo_usuario,
            area,
            fecha_ingreso,
            password
        )

        if insertar_personal(personal):
            flash("Cuenta creada correctamente. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("login"))

        flash("Error al crear la cuenta. Verifica que el DNI o correo no estén registrados.", "error")
        return redirect(url_for("registro"))

    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("registro"))


# =========================================================
# MAQUINARIA - ADMINISTRADOR
# =========================================================

@app.route("/registro_maquinaria")
def registro_maquinaria():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not es_supervisor_o_admin():
        flash("No tienes permisos para registrar maquinaria.", "error")
        return redirect(url_for("dashboard"))

    return render_template("maquinaria/registro_maquinaria.html")

@app.route("/api_listarmaquinarias", methods=['POST'])
def api_listarmaquinarias():
    try:
        resultado = listar_maquinarias()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": repr(e)})


@app.route("/guardar_maquinaria", methods=["POST"])
def guardar_maquinaria():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not es_supervisor_o_admin():
        flash("No tienes permisos para registrar maquinaria.", "error")
        return redirect(url_for("dashboard"))

    try:
        maquinaria = clsMaquinaria(
            request.form["nombre_codigo"],
            request.form["tipo"],
            request.form["marca"],
            request.form["modelo"],
            request.form["area"],
            request.form["estado"],
            request.form["observaciones"]
        )

        if insertar_maquinaria(maquinaria):
            flash("Maquinaria registrada correctamente.", "success")
            return redirect(url_for("mis_maquinarias"))

        flash("Error al registrar la maquinaria.", "error")
        return redirect(url_for("registro_maquinaria"))

    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("registro_maquinaria"))

@app.route("/api_guardar_maquinaria", methods=["POST"])
def api_guardar_maquinaria():
    try:
        data = request.json

        objMaquinaria = clsMaquinaria(
            0,
            data["nombre_codigo"],
            data["tipo"],
            data["marca"],
            data["modelo"],
            data["area"],
            data["estado"],
            data["observaciones"]
        )

        if insertar_maquinaria(objMaquinaria):
            return jsonify({
                "code": 1,
                "data": {},
                "message": "Maquinaria insertada correctamente"
            })

        return jsonify({
            "code": 0,
            "data": {},
            "message": "Error al insertar maquinaria"
        })

    except Exception as e:
        return jsonify({
            "code": -1,
            "data": {},
            "message": repr(e)
        })


@app.route("/mis_maquinarias")
def mis_maquinarias():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not es_supervisor_o_admin():
        flash("No tienes permisos para ver maquinaria.", "error")
        return redirect(url_for("dashboard"))

    try:
        maquinarias = listar_maquinarias()
        return render_template("maquinaria/mis_maquinarias.html", maquinarias=maquinarias)

    except Exception as e:
        flash(f"Error al cargar el inventario: {repr(e)}", "error")
        return redirect(url_for("dashboard"))


@app.route("/actualizar_maquinaria", methods=["POST"])
def actualizar_maquinaria_web():

    try:

        resultado = actualizar_maquinaria(
            request.form["id_maquinaria"],
            request.form["estado"]
        )

        if resultado:
            flash("Estado actualizado correctamente.", "success")
        else:
            flash("No se pudo actualizar.", "error")

    except Exception as e:
        flash(f"Error: {repr(e)}", "error")

    return redirect(url_for("mis_maquinarias"))
@app.route("/eliminar_maquinaria", methods=["POST"])
def eliminar_maquinaria_web():

    try:

        id_maquinaria = request.form["id_maquinaria"]

        maquinaria = obtener_maquinaria(id_maquinaria)

        if not maquinaria:
            flash("La maquinaria no existe.", "error")
            return redirect(url_for("mis_maquinarias"))

        if maquinaria["estado"] == "Operativo":
            flash(
                "No se puede eliminar una maquinaria operativa.",
                "error"
            )
            return redirect(url_for("mis_maquinarias"))

        if eliminar_maquinaria(id_maquinaria):
            flash(
                "Maquinaria eliminada correctamente.",
                "success"
            )
        else:
            flash(
                "No se pudo eliminar la maquinaria.",
                "error"
            )

    except Exception as e:
        flash(f"Error: {repr(e)}", "error")

    return redirect(url_for("mis_maquinarias"))
# =========================================================
# =========================================================
# SOLICITUDES - OPERARIO
# =========================================================

@app.route("/registrar_solicitud")
def registrar_solicitud():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not es_operario():
        flash("No tienes permisos para registrar solicitudes.", "error")
        return redirect(url_for("dashboard"))

    return render_template(
        "solicitudes/registrar_solicitud.html",
        trabajador=nombre_usuario_actual()
    )


@app.route("/guardar_solicitud", methods=["POST"])
def guardar_solicitud():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not es_operario():
        flash("No tienes permisos para registrar solicitudes.", "error")
        return redirect(url_for("dashboard"))

    try:
        solicitud = clsSolicitud(
            nombre_usuario_actual(),
            request.form["descripcion"],
            request.form["area"],
            request.form["prioridad"]
        )

        if insertar_solicitud(solicitud):
            flash("Solicitud registrada correctamente.", "success")
        else:
            flash("Error al registrar la solicitud.", "error")

        return redirect(url_for("mis_solicitudes"))

    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("registrar_solicitud"))


@app.route("/mis_solicitudes")
def mis_solicitudes():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not es_operario():
        flash("No tienes permisos para ver solicitudes.", "error")
        return redirect(url_for("dashboard"))

    solicitudes = listar_mis_solicitudes(nombre_usuario_actual())

    return render_template(
        "solicitudes/mis_solicitudes.html",
        solicitudes=solicitudes
    )


# =========================================================
# =========================================================
# SOLICITUDES - SUPERVISOR / ADMINISTRADOR
# =========================================================

@app.route("/gestion_solicitudes")
def gestion_solicitudes():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not es_supervisor_o_admin():
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for("dashboard"))

    estado = request.args.get("estado")
    area = request.args.get("area")
    prioridad = request.args.get("prioridad")

    solicitudes = listar_todas_solicitudes(estado, area, prioridad)

    return render_template(
        "solicitudes/gestion_solicitudes.html",
        solicitudes=solicitudes,
        estado=estado,
        area=area,
        prioridad=prioridad
    )


@app.route("/actualizar_solicitud", methods=["POST"])
def actualizar_solicitud_estado():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not es_supervisor_o_admin():
        flash("No tienes permisos para actualizar solicitudes.", "error")
        return redirect(url_for("dashboard"))

    try:
        id_solicitud = request.form["id_solicitud"]
        estado = request.form["estado"]
        comentario = request.form["comentario"]

        if actualizar_solicitud(id_solicitud, estado, comentario):
            flash("Solicitud actualizada correctamente.", "success")
        else:
            flash("Error al actualizar la solicitud.", "error")

        return redirect(url_for("gestion_solicitudes"))

    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("gestion_solicitudes"))


# =========================================================
# =========================================================
# ACTIVIDAD MAQUINARIA - OPERARIO / SUPERVISOR / ADMINISTRADOR
# =========================================================

@app.route("/actividad_maquinaria")
def actividad_maquinaria():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not usuario_logueado():
        flash("No tienes permisos para acceder a actividad de maquinaria.", "error")
        return redirect(url_for("dashboard"))

    actividades = listar_actividades_activas()
    return render_template("actividad/listado.html", actividades=actividades)


@app.route("/actividad/checkin")
def checkin_actividad():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not usuario_logueado():
        flash("No tienes permisos para iniciar actividad de maquinaria.", "error")
        return redirect(url_for("dashboard"))

    return render_template("actividad/checkin.html")


@app.route("/guardar_checkin", methods=["POST"])
def guardar_checkin():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not usuario_logueado():
        flash("No tienes permisos para iniciar actividad de maquinaria.", "error")
        return redirect(url_for("dashboard"))

    try:
        actividad = clsActividad(
            request.form["maquina"],
            request.form["zona"],
            request.form["combustible_inicial"],
            request.form["horas_estimadas"]
        )

        id_viaje = iniciar_actividad(actividad)

        if id_viaje:
            flash("Jornada iniciada correctamente.", "success")
            return redirect(url_for("monitoreo_activo", id_actividad=id_viaje))

        flash("Error al iniciar la jornada.", "error")
        return redirect(url_for("checkin_actividad"))

    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("checkin_actividad"))


@app.route("/actividad/activo/<int:id_actividad>")
def monitoreo_activo(id_actividad):
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not usuario_logueado():
        flash("No tienes permisos para monitorear maquinaria.", "error")
        return redirect(url_for("dashboard"))

    actividad = obtener_actividad(id_actividad)

    if actividad:
        return render_template("actividad/checkout.html", actividad=actividad)

    flash("Actividad no encontrada.", "error")
    return redirect(url_for("actividad_maquinaria"))


@app.route("/guardar_checkout/<int:id_actividad>", methods=["POST"])
def guardar_checkout(id_actividad):
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))

    if not usuario_logueado():
        flash("No tienes permisos para finalizar actividad de maquinaria.", "error")
        return redirect(url_for("dashboard"))

    try:
        accion = request.form.get("accion")

        if accion == "averia":
            estado = "AVERIADO"
            falla = request.form.get("observacion_falla", "")
            finalizar_actividad(id_actividad, None, None, None, estado, falla)
            flash("Alerta de avería registrada. Logística notificada.", "error")
        else:
            estado = "FINALIZADO"
            c_final = request.form["combustible_final"]
            h_reales = request.form["horas_reales"]
            motivo = request.form.get("motivo_retraso", "")

            finalizar_actividad(id_actividad, c_final, h_reales, motivo, estado, None)
            flash("Jornada finalizada y máquina liberada correctamente.", "success")

        return redirect(url_for("actividad_maquinaria"))

    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("actividad_maquinaria"))


# =========================================================
# API PERSONAL
# =========================================================

@app.route("/api_listarpersonal", methods=["POST"])
def api_listarpersonal():
    try:
        resultado = listar_personal()
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            "code": -1,
            "data": [],
            "error": "Excepción superior: " + repr(e)
        })


@app.route("/api_buscarpersonal/<string:dni>")
def api_buscarpersonal(dni):
    try:
        resultado = leer_personal_xDNI(dni)

        if resultado:
            return jsonify({
                "code": 1,
                "data": resultado,
                "message": "Personal encontrado."
            })

        return jsonify({
            "code": 0,
            "data": {},
            "message": f"No se encontró personal con DNI {dni}."
        })

    except Exception as e:
        return jsonify({
            "code": -1,
            "data": {},
            "error": "Excepción superior: " + repr(e)
        })


@app.route("/api_guardarpersonal", methods=["POST"])
def api_guardarpersonal():
    try:
        obj_personal = clsPersonal(
            request.json["dni"],
            request.json["nombres"],
            request.json["apellidos"],
            request.json.get("telefono", ""),
            request.json.get("correo", ""),
            request.json["tipo_usuario"],
            request.json["area"],
            request.json["fecha_ingreso"],
            request.json["password"]
        )

        if insertar_personal(obj_personal):
            return jsonify({
                "code": 1,
                "data": {},
                "message": "Personal insertado correctamente."
            })

        return jsonify({
            "code": 0,
            "data": {},
            "error": "Error al insertar personal."
        })

    except Exception as e:
        return jsonify({
            "code": -1,
            "data": {},
            "error": "Excepción superior: " + repr(e)
        })


# =========================================================
# API SOLICITUDES
# =========================================================

@app.route("/api_gestion_solicitudes")
def api_gestion_solicitudes():
    try:
        resultado = listar_todas_solicitudes()

        return jsonify({
            "code": 1,
            "data": resultado,
            "message": "Solicitudes listadas correctamente"
        })

    except Exception as e:
        return jsonify({
            "code": -1,
            "data": [],
            "error": "Excepción superior: " + repr(e)
        })


@app.route("/api_guardarsolicitud", methods=["POST"])
def api_guardarsolicitud():
    try:
        obj_solicitud = clsSolicitud(
            request.json["trabajador"],
            request.json["descripcion"],
            request.json["area"],
            request.json["prioridad"]
        )

        if insertar_solicitud(obj_solicitud):
            return jsonify({
                "code": 1,
                "data": {},
                "message": "Solicitud insertada correctamente"
            })

        return jsonify({
            "code": 0,
            "data": {},
            "error": "Error al insertar solicitud"
        })

    except Exception as e:
        return jsonify({
            "code": -1,
            "data": {},
            "error": "Excepción superior: " + repr(e)
        })


if __name__ == "__main__":
    app.run(debug=True)