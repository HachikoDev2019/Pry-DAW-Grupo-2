from flask import Flask, render_template, request, redirect, url_for, flash, session
from maquinariaAD import clsMaquinaria, insertar_maquinaria, listar_maquinarias
from solicitudAD import (clsSolicitud, insertar_solicitud, listar_mis_solicitudes, listar_todas_solicitudes, actualizar_solicitud)
from personalAD import clsPersonal, insertar_personal, verificar_credenciales
from actividadAD import clsActividad, iniciar_actividad, listar_actividades_activas, obtener_actividad, finalizar_actividad

from bd import obtener_conexion


app = Flask(__name__)
app.secret_key = "pomalca_secret_key"

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        dni_ingresado = request.form.get('dni', '').strip()
        password_ingresada = request.form.get('password', '').strip()

        trabajador = verificar_credenciales(dni_ingresado, password_ingresada)

        if trabajador:
    
            session['id_personal'] = trabajador['id_personal']
            session['nombres'] = trabajador['nombres']
            session['apellidos'] = trabajador['apellidos']
            session['tipo_usuario'] = trabajador['tipo_usuario']
            
            flash(f"¡Bienvenido, {trabajador['nombres']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Número de DNI o contraseña incorrectos, o usuario inactivo.", "error")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if 'id_personal' not in session:
        flash("Por favor, inicie sesión para acceder al portal.", "error")
        return redirect(url_for('login'))
        
    return render_template("dashboard.html")


@app.route("/registro_persona")
def registropersona():
    return render_template("registro.html")


@app.route("/registro_maquinaria")
def registro_maquinaria():
    return render_template("maquinaria/registro_maquinaria.html")


@app.route("/guardar_maquinaria", methods=["POST"])
def guardar_maquinaria():
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
    

@app.route("/mis_maquinarias")
def mis_maquinarias():
    try:
        maquinarias = listar_maquinarias()
        return render_template(
            "maquinaria/mis_maquinarias.html", 
            maquinarias=maquinarias
        )
    except Exception as e:
        flash(f"Error al cargar el inventario: {repr(e)}", "error")
        return redirect(url_for("dashboard"))


    
@app.route("/registrar_solicitud")
def registrar_solicitud():
    return render_template("solicitudes/registrar_solicitud.html")


@app.route("/guardar_solicitud", methods=["POST"])
def guardar_solicitud():
    try:
        solicitud = clsSolicitud(
            request.form["trabajador"],
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
    trabajador = "Trabajador Demo"
    solicitudes = listar_mis_solicitudes(trabajador)

    return render_template(
        "solicitudes/mis_solicitudes.html",
        solicitudes=solicitudes
    )

@app.route("/gestion_solicitudes")
def gestion_solicitudes():
    if session.get('tipo_usuario') != 'Administrador':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('dashboard'))
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
    
@app.route("/registro")
def registro():
    return render_template("registro.html")
 
 
@app.route("/guardar_personal", methods=["POST"])
def guardar_personal():
    try:
        personal = clsPersonal(
            request.form["dni"].strip(),
            request.form["nombres"].strip(),
            request.form["apellidos"].strip(),
            request.form["telefono"].strip(),
            request.form["correo"].strip(),
            request.form["password"].strip(),
            request.form["tipo_usuario"],
            request.form["area"],
            request.form["puesto"],
            request.form["fecha_ingreso"]
        )
 
        if insertar_personal(personal):
            flash("Cuenta creada correctamente.", "success")
            return redirect(url_for("registro"))
 
        flash("Error al crear la cuenta.", "error")
        return redirect(url_for("registro"))
 
    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("registro"))

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for('login'))

# RUTAS: ACTIVIDAD MAQUINARIA (NUEVO MÓDULO)
# ==========================================


@app.route("/actividad_maquinaria")
def actividad_maquinaria():
    # Lista general de actividades (Panel de Monitoreo)
    actividades = listar_actividades_activas()
    return render_template("actividad/listado.html", actividades=actividades)


@app.route("/actividad/checkin")
def checkin_actividad():
    # Muestra el formulario para iniciar jornada
    return render_template("actividad/checkin.html")


@app.route("/guardar_checkin", methods=["POST"])
def guardar_checkin():
    # Guarda el inicio de jornada y redirige al panel de la máquina
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
    # Muestra el panel activo de una máquina específica (para hacer Checkout o SOS)
    actividad = obtener_actividad(id_actividad)
    if actividad:
        return render_template("actividad/checkout.html", actividad=actividad)
    
    flash("Actividad no encontrada.", "error")
    return redirect(url_for("actividad_maquinaria"))


@app.route("/guardar_checkout/<int:id_actividad>", methods=["POST"])
def guardar_checkout(id_actividad):
    # Procesa el Fin de Jornada o el reporte de Avería
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





if __name__ == "__main__":
    app.run(debug=True)