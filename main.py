import json
import math
import os
from datetime import datetime
import requests
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from pdf_generator import generar_pdf_solicitud

# =========================================================
# IMPORTACIÓN DE MÓDULOS DE ACCESO A DATOS (AD)
# =========================================================
from maquinariaAD import (
    clsMaquinaria, 
    insertar_maquinaria, 
    listar_maquinarias, 
    actualizar_maquinaria, 
    eliminar_maquinaria, 
    obtener_maquinaria, 
    leer_maquinaria_xId
)

from solicitudAD import (
    clsSolicitud,
    insertar_solicitud,
    listar_mis_solicitudes,
    listar_todas_solicitudes,
    actualizar_solicitud,
    eliminar_solicitud,
    actualizar_solicitud_operario,
    actualizar_ruta_pdf,
    actualizar_ruta_pdf_firmado
)

from personalAD import (
    clsPersonal,
    insertar_personal,
    verificar_credenciales,
    listar_personal,
    leer_personal_xDNI,
    guardar_face_descriptor,
    obtener_todos_descriptores_activos,
    actualizar_personal, # NUEVO
    eliminar_personal    # NUEVO
)

from actividadAD import (
    clsActividad,
    iniciar_actividad,
    listar_actividades_activas,
    obtener_actividad,
    finalizar_actividad,
    eliminar_actividad   # NUEVO
)

app = Flask(__name__)
app.secret_key = "pomalca_secret_key"

EXTENSIONES_PERMITIDAS = {"pdf"}

def extension_permitida(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


# =========================================================
# FUNCIONES AUXILIARES DE SESIÓN
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
# VISTAS: LOGIN / LOGOUT / DASHBOARD
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

@app.route("/dashboard")
def dashboard():
    if not usuario_logueado():
        flash("Por favor, inicie sesión para acceder al portal.", "error")
        return redirect(url_for("login"))
    return render_template("dashboard.html")


# =========================================================
# VISTAS: PERSONAL
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
        personal = clsPersonal(dni, nombres, apellidos, telefono, correo, tipo_usuario, area, fecha_ingreso, password)
        if insertar_personal(personal):
            # Si el usuario capturó su rostro durante el registro, guardarlo
            face_raw = request.form.get("face_descriptor", "").strip()
            if face_raw:
                try:
                    descriptor = json.loads(face_raw)
                    if len(descriptor) == 128:
                        usuario_nuevo = leer_personal_xDNI(dni)
                        if usuario_nuevo:
                            guardar_face_descriptor(usuario_nuevo["id_personal"], face_raw)
                except Exception:
                    pass  # El rostro falla silenciosamente; la cuenta igual se crea

            flash("Cuenta creada correctamente. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("login"))
        flash("Error al crear la cuenta. Verifica que el DNI o correo no estén registrados.", "error")
        return redirect(url_for("registro"))
    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("registro"))


# =========================================================
# VISTAS: MAQUINARIA
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
            request.form["nombre_codigo"], request.form["tipo"], request.form["marca"],
            request.form["modelo"], request.form["area"], request.form["estado"], request.form["observaciones"]
        )
        if insertar_maquinaria(maquinaria):
            flash("Maquinaria registrada correctamente.", "success")
            return redirect(url_for("mis_maquinarias"))
        flash("Error al registrar la maquinaria.", "error")
        return redirect(url_for("registro_maquinaria"))
    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("registro_maquinaria"))

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
        resultado = actualizar_maquinaria(request.form["id_maquinaria"], request.form["estado"])
        flash("Estado actualizado correctamente." if resultado else "No se pudo actualizar.", "success" if resultado else "error")
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
            flash("No se puede eliminar una maquinaria operativa.", "error")
            return redirect(url_for("mis_maquinarias"))
        flash("Maquinaria eliminada correctamente." if eliminar_maquinaria(id_maquinaria) else "No se pudo eliminar.", "success" if eliminar_maquinaria(id_maquinaria) else "error")
    except Exception as e:
        flash(f"Error: {repr(e)}", "error")
    return redirect(url_for("mis_maquinarias"))


# =========================================================
# VISTAS: SOLICITUDES
# =========================================================
@app.route("/registrar_solicitud")
def registrar_solicitud():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))
    if not es_operario():
        flash("No tienes permisos para registrar solicitudes.", "error")
        return redirect(url_for("dashboard"))
    return render_template("solicitudes/registrar_solicitud.html", trabajador=nombre_usuario_actual())

@app.route("/guardar_solicitud", methods=["POST"])
def guardar_solicitud():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))
    if not es_operario():
        flash("No tienes permisos para registrar solicitudes.", "error")
        return redirect(url_for("dashboard"))
    try:
        solicitud = clsSolicitud(nombre_usuario_actual(), request.form["descripcion"], request.form["area"], request.form["prioridad"])
        id_solicitud = insertar_solicitud(solicitud)
        if id_solicitud:
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
    return render_template("solicitudes/mis_solicitudes.html", solicitudes=solicitudes)

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

    return render_template("solicitudes/gestion_solicitudes.html", solicitudes=solicitudes, estado=estado, area=area, prioridad=prioridad)

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
            if estado == "Aprobado":
                solicitudes = listar_todas_solicitudes()
                solicitud = next((s for s in solicitudes if str(s["id_solicitud"]) == str(id_solicitud)), None)
                if solicitud:
                    ruta_pdf = generar_pdf_solicitud(id_solicitud, solicitud["trabajador"], solicitud["descripcion"], solicitud["area"], solicitud["prioridad"])
                    actualizar_ruta_pdf(id_solicitud, ruta_pdf)
                    flash("Solicitud aprobada y PDF generado correctamente.", "success")
                else:
                    flash("Solicitud aprobada, pero no se pudo generar el PDF.", "warning")
            else:
                flash("Solicitud actualizada correctamente.", "success")
        else:
            flash("Error al actualizar la solicitud.", "error")
        return redirect(url_for("gestion_solicitudes"))
    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("gestion_solicitudes"))

@app.route("/actualizar_solicitud_operario", methods=["POST"])
def actualizar_solicitud_operario_route():
    if not usuario_logueado() or not es_operario():
        flash("No tienes permisos para actualizar solicitudes.", "error")
        return redirect(url_for("mis_solicitudes"))
    try:
        id_solicitud = request.form["id_solicitud"]
        descripcion = request.form.get("descripcion", "").strip()
        area = request.form.get("area", "")
        prioridad = request.form.get("prioridad", "")

        if not descripcion or not area or not prioridad:
            flash("Complete todos los campos obligatorios.", "error")
            return redirect(url_for("mis_solicitudes"))

        status = actualizar_solicitud_operario(id_solicitud, descripcion, area, prioridad)
        flash("Solicitud actualizada correctamente." if status else "Error al actualizar.", "success" if status else "error")
        return redirect(url_for("mis_solicitudes"))
    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("mis_solicitudes"))

@app.route("/eliminar_solicitud", methods=["POST"])
def eliminar_solicitud_web():
    if not usuario_logueado() or not es_operario():
        flash("No tienes permisos para eliminar solicitudes.", "error")
        return redirect(url_for("mis_solicitudes"))
    try:
        id_solicitud = request.form.get("id_solicitud")
        flash("Solicitud Web eliminada." if eliminar_solicitud(id_solicitud) else "Error al eliminar.", "success" if eliminar_solicitud(id_solicitud) else "error")
        return redirect(url_for("mis_solicitudes"))
    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("mis_solicitudes"))

@app.route("/generar_pdf/<int:id_solicitud>", methods=["POST"])
def generar_pdf_existente(id_solicitud):
    if not usuario_logueado() or not es_supervisor_o_admin():
        flash("No autorizado.", "error")
        return redirect(url_for("dashboard"))
    try:
        solicitudes = listar_todas_solicitudes()
        solicitud = next((s for s in solicitudes if s["id_solicitud"] == id_solicitud), None)
        if not solicitud or solicitud["estado"] != "Aprobado":
            flash("La solicitud no existe o no está aprobada.", "error")
            return redirect(url_for("gestion_solicitudes"))

        ruta_pdf = generar_pdf_solicitud(id_solicitud, solicitud["trabajador"], solicitud["descripcion"], solicitud["area"], solicitud["prioridad"])
        actualizar_ruta_pdf(id_solicitud, ruta_pdf)
        flash("PDF generado correctamente.", "success")
    except Exception as e:
        flash(f"Error al generar el PDF: {repr(e)}", "error")
    return redirect(url_for("gestion_solicitudes"))

@app.route("/subir_pdf_firmado/<int:id_solicitud>", methods=["POST"])
def subir_pdf_firmado(id_solicitud):
    if not usuario_logueado() or not es_supervisor_o_admin():
        flash("No autorizado.", "error")
        return redirect(url_for("dashboard"))
    archivo = request.files.get("pdf_firmado")
    if not archivo or archivo.filename == "":
        flash("No se seleccionó ningún archivo.", "error")
        return redirect(url_for("gestion_solicitudes"))
    if not extension_permitida(archivo.filename):
        flash("Solo se permiten archivos PDF.", "error")
        return redirect(url_for("gestion_solicitudes"))
    try:
        carpeta = "static/documentos/firmados"
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
        nombre_archivo = f"solicitud_{id_solicitud}_firmado.pdf"
        ruta = os.path.join(carpeta, nombre_archivo)
        archivo.save(ruta)
        if actualizar_ruta_pdf_firmado(id_solicitud, ruta):
            flash("PDF firmado subido correctamente.", "success")
        else:
            flash("Error al guardar la ruta del PDF.", "error")
    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
    return redirect(url_for("gestion_solicitudes"))


# =========================================================
# VISTAS: ACTIVIDAD MAQUINARIA
# =========================================================
@app.route("/actividad_maquinaria")
def actividad_maquinaria():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))
    actividades = listar_actividades_activas()
    return render_template("actividad/listado.html", actividades=actividades)

@app.route("/actividad/checkin")
def checkin_actividad():
    if not usuario_logueado() or not es_operario():
        flash("Solo los Operarios pueden hacer el Check-In.", "error")
        return redirect(url_for("actividad_maquinaria"))
    todas_las_maquinas = listar_maquinarias()
    maquinas_disponibles = [m for m in todas_las_maquinas if m["estado"] == "Operativo"]
    return render_template("actividad/checkin.html", maquinas=maquinas_disponibles)

@app.route("/guardar_checkin", methods=["POST"])
def guardar_checkin():
    if not usuario_logueado() or not es_operario():
        flash("Acceso denegado.", "error")
        return redirect(url_for("dashboard"))
    try:
        actividad = clsActividad(request.form["maquina"], request.form["zona"], request.form["combustible_inicial"], request.form["horas_estimadas"])
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
        return redirect(url_for("login"))
    actividad = obtener_actividad(id_actividad)
    if actividad:
        return render_template("actividad/checkout.html", actividad=actividad)
    flash("Actividad no encontrada.", "error")
    return redirect(url_for("actividad_maquinaria"))

@app.route("/guardar_checkout/<int:id_actividad>", methods=["POST"])
def guardar_checkout(id_actividad):
    if not usuario_logueado():
        return redirect(url_for("login"))
    try:
        accion = request.form.get("accion")
        if accion == "averia":
            finalizar_actividad(id_actividad, None, None, None, "AVERIADO", request.form.get("observacion_falla", ""))
            flash("Alerta de avería registrada. Logística notificada.", "error")
        else:
            finalizar_actividad(id_actividad, request.form["combustible_final"], request.form["horas_reales"], request.form.get("motivo_retraso", ""), "FINALIZADO", None)
            flash("Jornada finalizada y máquina liberada.", "success")
        return redirect(url_for("actividad_maquinaria"))
    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("actividad_maquinaria"))


# ==============================================================================
#                      COLECCIÓN ÚNICA DE APIS REST (JSON)
# ==============================================================================

def obtener_id_solicitado(campo_id):
    """Función helper para leer IDs de forma segura desde GET o POST (JSON/Form)"""
    if request.method == "POST":
        if request.is_json and request.json:
            return request.json.get(campo_id)
        return request.form.get(campo_id)
    return request.args.get(campo_id)


# ---------------------------------------------------------
# APIS: MAQUINARIA
# ---------------------------------------------------------
@app.route("/api_guardarmaquinaria", methods=["POST"])
def api_guardarmaquinaria():
    try:
        data = request.json
        obj = clsMaquinaria(data["nombre_codigo"], data["tipo"], data["marca"], data["modelo"], data["area"], data["estado"], data["observaciones"])
        if insertar_maquinaria(obj):
            return jsonify({"code": 1, "data": {}, "message": "Maquinaria insertada correctamente"})
        return jsonify({"code": 0, "data": {}, "message": "Error al insertar maquinaria"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_actualizarmaquinaria", methods=["POST"])
def api_actualizarmaquinaria():
    try:
        data = request.json
        if actualizar_maquinaria(data["id_maquinaria"], data["estado"]):
            return jsonify({"code": 1, "data": {}, "message": "Maquinaria actualizada correctamente"})
        return jsonify({"code": 0, "data": {}, "message": "No se pudo actualizar la maquinaria"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_eliminarmaquinaria", methods=["POST"])
def api_eliminarmaquinaria():
    try:
        id_m = request.json.get("id_maquinaria")
        if eliminar_maquinaria(id_m):
            return jsonify({"code": 1, "data": {}, "message": "Maquinaria eliminada correctamente"})
        return jsonify({"code": 0, "data": {}, "message": "No se pudo eliminar la maquinaria"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_leermaquinariaxid", methods=["GET", "POST"])
def api_leermaquinariaxid():
    try:
        id_entidad = obtener_id_solicitado("id_maquinaria")
        resultado = leer_maquinaria_xId(id_entidad)
        if resultado:
            return jsonify({"code": 1, "data": resultado, "message": "Maquinaria encontrada"})
        return jsonify({"code": 0, "data": [], "message": "No se encontró la maquinaria"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_leermaquinarias", methods=["GET"])
def api_leermaquinarias():
    try:
        return jsonify({"code": 1, "data": listar_maquinarias(), "message": "Listado de maquinarias obtenido"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})


# ---------------------------------------------------------
# APIS: PERSONAL
# ---------------------------------------------------------
@app.route("/api_guardarpersonal", methods=["POST"])
def api_guardarpersonal():
    try:
        data = request.json
        obj = clsPersonal(data["dni"], data["nombres"], data["apellidos"], data.get("telefono", ""), data.get("correo", ""), data["tipo_usuario"], data["area"], data["fecha_ingreso"], data["password"])
        if insertar_personal(obj):
            return jsonify({"code": 1, "data": {}, "message": "Personal insertado correctamente"})
        return jsonify({"code": 0, "data": {}, "message": "Error al insertar personal"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_actualizarpersonal", methods=["POST"])
def api_actualizarpersonal():
    try:
        data = request.json
        if actualizar_personal(data["id_personal"], data):
            return jsonify({"code": 1, "data": {}, "message": "Personal actualizado correctamente"})
        return jsonify({"code": 0, "data": {}, "message": "No se pudo actualizar el personal"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_eliminarpersonal", methods=["POST"])
def api_eliminarpersonal():
    try:
        id_p = request.json.get("id_personal")
        if eliminar_personal(id_p):
            return jsonify({"code": 1, "data": {}, "message": "Personal eliminado correctamente"})
        return jsonify({"code": 0, "data": {}, "message": "No se pudo eliminar el personal"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_leerpersonalxid", methods=["GET", "POST"])
def api_leerpersonalxid():
    try:
        dni_p = obtener_id_solicitado("dni") or obtener_id_solicitado("id_personal")
        resultado = leer_personal_xDNI(dni_p)
        if resultado:
            return jsonify({"code": 1, "data": resultado, "message": "Personal encontrado"})
        return jsonify({"code": 0, "data": [], "message": "No se encontró el personal"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_leerpersonal", methods=["GET"])
def api_leerpersonal():
    try:
        return jsonify({"code": 1, "data": listar_personal(), "message": "Listado de personal obtenido"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})


# ---------------------------------------------------------
# APIS: SOLICITUDES
# ---------------------------------------------------------
@app.route("/api_guardarsolicitud", methods=["POST"])
def api_guardarsolicitud():
    try:
        data = request.json
        obj = clsSolicitud(data["trabajador"], data["descripcion"], data["area"], data["prioridad"])
        if insertar_solicitud(obj):
            return jsonify({"code": 1, "data": {}, "message": "Solicitud insertada correctamente"})
        return jsonify({"code": 0, "data": {}, "message": "Error al insertar solicitud"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_actualizarsolicitud", methods=["POST"])
def api_actualizarsolicitud():
    try:
        data = request.json
        if actualizar_solicitud(data["id_solicitud"], data["estado"], data["comentario"]):
            return jsonify({"code": 1, "data": {}, "message": "Solicitud actualizada correctamente"})
        return jsonify({"code": 0, "data": {}, "message": "No se pudo actualizar la solicitud"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_eliminarsolicitud", methods=["POST"])
def api_eliminarsolicitud():
    try:
        id_s = request.json.get("id_solicitud")
        if eliminar_solicitud(id_s):
            return jsonify({"code": 1, "data": {}, "message": "Solicitud eliminada correctamente"})
        return jsonify({"code": 0, "data": {}, "message": "No se pudo eliminar la solicitud"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_leersolicitudxid", methods=["GET", "POST"])
def api_leersolicitudxid():
    try:
        id_entidad = obtener_id_solicitado("id_solicitud")
        solicitudes = listar_todas_solicitudes()
        resultado = next((s for s in solicitudes if str(s["id_solicitud"]) == str(id_entidad)), None)
        
        if resultado:
            return jsonify({"code": 1, "data": resultado, "message": "Solicitud encontrada"})
        return jsonify({"code": 0, "data": [], "message": "No se encontró la solicitud"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_leersolicitudes", methods=["GET"])
def api_leersolicitudes():
    try:
        return jsonify({"code": 1, "data": listar_todas_solicitudes(), "message": "Listado de solicitudes obtenido"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})


# ---------------------------------------------------------
# APIS: ACTIVIDAD
# ---------------------------------------------------------
@app.route("/api_guardaractividad", methods=["POST"])
def api_guardaractividad():
    try:
        data = request.json
        obj = clsActividad(data["maquina"], data["zona"], data["combustible_inicial"], data["horas_estimadas"])
        id_act = iniciar_actividad(obj)
        if id_act:
            return jsonify({"code": 1, "data": {"id_actividad": id_act}, "message": "Actividad iniciada correctamente"})
        return jsonify({"code": 0, "data": {}, "message": "Error al iniciar actividad"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_actualizaractividad", methods=["POST"])
def api_actualizaractividad():
    try:
        data = request.json
        finalizar_actividad(data["id_actividad"], data.get("combustible_final"), data.get("horas_reales"), data.get("motivo_retraso"), data.get("estado", "FINALIZADO"), data.get("observacion_falla"))
        return jsonify({"code": 1, "data": {}, "message": "Actividad actualizada correctamente"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_eliminaractividad", methods=["POST"])
def api_eliminaractividad():
    try:
        id_a = request.json.get("id_actividad")
        if eliminar_actividad(id_a):
            return jsonify({"code": 1, "data": {}, "message": "Actividad eliminada correctamente"})
        return jsonify({"code": 0, "data": {}, "message": "No se pudo eliminar la actividad"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_leeractividadxid", methods=["GET", "POST"])
def api_leeractividadxid():
    try:
        id_entidad = obtener_id_solicitado("id_actividad")
        resultado = obtener_actividad(id_entidad)
        if resultado:
            return jsonify({"code": 1, "data": resultado, "message": "Actividad encontrada"})
        return jsonify({"code": 0, "data": [], "message": "No se encontró la actividad"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})

@app.route("/api_leeractividades", methods=["GET"])
def api_leeractividades():
    try:
        return jsonify({"code": 1, "data": listar_actividades_activas(), "message": "Listado de actividades activas obtenido"})
    except Exception as e:
        return jsonify({"code": -1, "data": [], "message": repr(e)})




# =========================================================
# RECONOCIMIENTO FACIAL
# =========================================================

def _distancia_euclidiana(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


@app.route("/registrar_rostro")
def registrar_rostro():
    if not usuario_logueado():
        flash("Debe iniciar sesión.", "error")
        return redirect(url_for("login"))
    return render_template("registro_rostro.html")


@app.route("/api/guardar_rostro", methods=["POST"])
def api_guardar_rostro():
    if not usuario_logueado():
        return jsonify({"code": 0, "message": "No autenticado."})
    try:
        descriptor = request.json.get("descriptor", [])
        if len(descriptor) != 128:
            return jsonify({"code": 0, "message": f"Descriptor inválido: {len(descriptor)} valores (se esperan 128)."})
        descriptor_json = json.dumps(descriptor)
        guardar_face_descriptor(session["id_personal"], descriptor_json)
        return jsonify({"code": 1, "message": "Rostro registrado correctamente."})
    except Exception as e:
        print("ERROR /api/guardar_rostro:", repr(e))
        return jsonify({"code": 0, "message": str(e)})


@app.route("/api/login_facial", methods=["POST"])
def api_login_facial():
    try:
        descriptor_input = request.json.get("descriptor", [])
        if len(descriptor_input) != 128:
            return jsonify({"code": 0, "message": "Descriptor inválido."})

        registros = obtener_todos_descriptores_activos()
        UMBRAL = 0.60
        mejor_match = None
        mejor_dist = float("inf")

        for reg in registros:
            descriptor_bd = json.loads(reg["face_descriptor"])
            dist = _distancia_euclidiana(descriptor_input, descriptor_bd)
            if dist < mejor_dist:
                mejor_dist = dist
                mejor_match = reg

        if mejor_match and mejor_dist < UMBRAL:
            session["id_personal"] = mejor_match["id_personal"]
            session["nombres"] = mejor_match["nombres"]
            session["apellidos"] = mejor_match["apellidos"]
            session["tipo_usuario"] = mejor_match["tipo_usuario"]
            return jsonify({
                "code": 1,
                "message": f"¡Bienvenido, {mejor_match['nombres']}!",
                "redirect": url_for("dashboard")
            })

        dist_info = f"{mejor_dist:.3f}" if mejor_match else "sin registros"
        return jsonify({"code": 0, "message": f"Rostro no reconocido (dist: {dist_info}). Intenta de nuevo."})
    except Exception as e:
        return jsonify({"code": -1, "message": repr(e)})


# =========================================================
# CHATBOT INTELIGENTE — Anthropic Claude
# =========================================================

CHATBOT_SYSTEM = """Eres el asistente virtual inteligente del Sistema de Gestión de la Azucarera Pomalca.
Tu rol es orientar a los usuarios sobre cómo usar la aplicación de forma clara, amable y concisa.

=== MÓDULOS DEL SISTEMA ===

1. SOLICITUDES
   - Operarios pueden registrar solicitudes de materiales o repuestos desde "Registrar Solicitud".
   - Campos: descripción, área, prioridad (Alta/Media/Baja).
   - Estados: Pendiente → En revisión → Aprobado / Rechazado.
   - Supervisores y Administradores gestionan y aprueban desde "Gestión de Solicitudes".
   - Un Operario puede editar o eliminar sus solicitudes si aún están Pendientes.

2. MAQUINARIA
   - Solo Supervisores y Administradores pueden registrar y gestionar maquinaria.
   - Estados de maquinaria: Operativo, En Mantenimiento, Inactivo.
   - No se puede eliminar maquinaria con estado "Operativo".
   - Se registra: nombre/código, tipo, marca, modelo, área, estado, observaciones.

3. ACTIVIDAD DE MAQUINARIA
   - Operarios realizan Check-In para iniciar una jornada con una máquina operativa.
   - Se registra: máquina, zona, combustible inicial, horas estimadas.
   - Al finalizar (Check-Out): combustible final, horas reales, motivo de retraso si aplica.
   - Si hay avería durante la jornada, se reporta y la máquina queda como AVERIADA.

4. RECONOCIMIENTO FACIAL
   - Cualquier usuario puede registrar su rostro desde "Mi Rostro" en el menú lateral.
   - Una vez registrado, puede iniciar sesión desde la pantalla de login sin contraseña.
   - Se recomienda buena iluminación y mirar directo a la cámara al registrar.

5. ROLES Y PERMISOS
   - Operario: registra solicitudes y actividades de maquinaria.
   - Supervisor: gestiona solicitudes, maquinaria y actividad.
   - Administrador: acceso completo a todo el sistema.

=== REGLAS DE RESPUESTA ===
- Responde siempre en español.
- Sé breve y directo (máximo 4 oraciones).
- Si el usuario pregunta algo fuera del sistema, redirige amablemente al tema del sistema.
- Usa listas cuando expliques varios pasos.
- Si no sabes algo específico del sistema, sugiere contactar al Administrador.
"""


@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    if not usuario_logueado():
        return jsonify({"respuesta": "Debes iniciar sesión para usar el asistente."})
    try:
        import anthropic
        data = request.json
        historial = data.get("historial", [])
        mensaje = data.get("mensaje", "").strip()

        if not mensaje:
            return jsonify({"respuesta": "Por favor escribe tu consulta."})

        # Agregar el nombre y rol del usuario al contexto
        nombre = session.get("nombres", "")
        rol = session.get("tipo_usuario", "")
        contexto_usuario = f"[Usuario actual: {nombre}, Rol: {rol}]"

        mensajes_api = []
        for h in historial[-10:]:  # últimos 10 turnos
            mensajes_api.append({"role": h["role"], "content": h["content"]})
        mensajes_api.append({"role": "user", "content": f"{contexto_usuario}\n{mensaje}"})

        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=CHATBOT_SYSTEM,
            messages=mensajes_api
        )
        return jsonify({"respuesta": response.content[0].text})

    except Exception as e:
        print("Error chatbot:", repr(e))
        return jsonify({"respuesta": "No puedo responder en este momento. Intenta de nuevo en unos segundos."})




## facturacion


@app.route('/facturacion')
def facturacion():
    return render_template('facturacion/facturacion.html')

SUNAT_API_URL = "https://facturaciondirecta.com/API_SUNAT/post.php"

@app.route('/facturacion/emitir', methods=['POST'])
def emitir_comprobante_sunat():
    try:
        # 1. Recibir los datos planos que vienen desde tu formulario HTML
        data_frontend = request.get_json()
        
        # Extraemos las variables del HTML
        tipo_doc = data_frontend.get('tipo_doc')  # "01" (Factura) o "03" (Boleta)
        doc_cliente = data_frontend.get('doc')     # DNI o RUC
        nombre_cliente = data_frontend.get('cliente')
        producto_nombre = data_frontend.get('producto')
        cantidad = float(data_frontend.get('cantidad', 0))
        precio_unitario = float(data_frontend.get('precio', 0))
        total = float(data_frontend.get('total', 0))
        fecha_emision = data_frontend.get('fecha')

        # --- CÁLCULOS TRIBUTARIOS ---
        # En tu JSON de ejemplo, la "total_gravada" es el subtotal (Total / 1.18)
        total_gravada = round(total / 1.18, 2)
        total_igv = round(total - total_gravada, 2)
        
        # El "precio_base" en tu JSON de ejemplo equivale al precio unitario SIN IGV
        precio_base = round(precio_unitario / 1.18, 2)

        # Hora actual para el campo 'hora_emision'
        hora_actual = datetime.now().strftime("%H:%M:%S")

        # Determinar tipo de entidad del cliente (6 = RUC, 1 = DNI)
        tipo_entidad = "6" if len(doc_cliente) == 11 else "1"

        # --- CONSTRUCCIÓN DEL JSON IGUAL A TU EJEMPLO ---
        payload_api = {
            "empresa": {
                "ruc": "20163898200",  # RUC de simulación de tu ejemplo
                "razon_social": "EMPRESA AGROINDUSTRIAL POMALCA S.A.A",
                "nombre_comercial": "POMALCA S.A.A",
                "domicilio_fiscal": "Car. Chiclayo a Chogoyape Km. 07 (frente a la iglesia de Pomalca)", # Usa los datos de tu empresa real o de pruebas
                "ubigeo": "140112",
                "urbanizacion": "ZONA INDUSTRIAL",
                "distrito": "POMALCA",
                "provincia": "CHICLAYO",
                "departamento": "LAMBAYEQUE",        
                "modo": "0",  # 0 suele ser Beta/Homologación, 1 es Producción
                "usu_secundario_produccion_user": "MODDATOS",
                "usu_secundario_produccion_password": "MODDATOS",
                "vendedor": "LAMBAYEQUE"   
                 
            },
            "cliente": {
                "razon_social_nombres": nombre_cliente,
                "numero_documento": doc_cliente,
                "codigo_tipo_entidad": tipo_entidad,
                "cliente_direccion": "Dirección por defecto"
            },
            "venta": {
                "serie": "FF03" if tipo_doc == "01" else "BB03", # Series de prueba según tipo
                "numero": "53953",  # En un entorno real, esto vendrá correlativo de tu Base de Datos
                "fecha_emision": fecha_emision,
                "hora_emision": hora_actual,
                "fecha_vencimiento": "",
                "moneda_id": "1",  # 1 suele ser Soles (PEN) en la mayoría de sistemas locales
                "forma_pago_id": "1", # 1 = Contado
                "total_gravada": str(total_gravada),
                "total_igv": str(total_igv),
                "total_exonerada": "",
                "total_inafecta": "",
                "tipo_documento_codigo": tipo_doc,  # "01" o "03"
                "nota": "Emisión desde Sistema Pomalca"
            },
            "items": [
                {
                    "producto": producto_nombre,
                    "cantidad": str(int(cantidad)),
                    "precio_base": str(precio_base),
                    "codigo_sunat": "43211503",  # Código estándar genérico
                    "codigo_producto": "POM-001",
                    "codigo_unidad": "NIU",      # Unidades comerciales
                    "tipo_igv_codigo": "10"      # 10 = Gravado - Operación Onerosa
                }
            ]
        }

        # 2. Enviar el JSON estructurado mediante POST a la API externa
        headers = {"Content-Type": "application/json"}
        respuesta_externa = requests.post(
            SUNAT_API_URL, 
            json=payload_api, 
            headers=headers, 
            timeout=15
        )

        # 3. Procesar respuesta de la API de Facturación
        try:
            resultado_json = respuesta_externa.json()
        except Exception:
            resultado_json = {"respuesta_texto": respuesta_externa.text}

        if respuesta_externa.status_code == 200:
            resultado_json = respuesta_externa.json()
            print("REPORTE DE LA API:", resultado_json)
            # Aquí puedes meter tu código PyMySQL para registrar la venta en tu Base de Datos local
            return jsonify({
                "status": "success",
                "sunat_response": resultado_json
            }), 200
        else:
            return jsonify({
                "status": "error",
                "error": f"La API SUNAT denegó la petición con código {respuesta_externa.status_code}",
                "detalles": resultado_json
            }), respuesta_externa.status_code

    except requests.exceptions.Timeout:
        return jsonify({"status": "error", "error": "Tiempo de espera agotado con la API de SUNAT."}), 504
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500







if __name__ == "__main__":
    app.run(debug=True)
