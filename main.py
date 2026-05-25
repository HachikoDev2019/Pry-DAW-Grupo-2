from flask import Flask, render_template, request, redirect, url_for, flash
from maquinariaAD import clsMaquinaria, insertar_maquinaria
from solicitudAD import (clsSolicitud, insertar_solicitud, listar_mis_solicitudes, listar_todas_solicitudes, actualizar_solicitud)

app = Flask(__name__)
app.secret_key = "pomalca_secret_key"


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


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
            return redirect(url_for("registro_maquinaria"))

        flash("Error al registrar la maquinaria.", "error")
        return redirect(url_for("registro_maquinaria"))

    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("registro_maquinaria"))
    
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


if __name__ == "__main__":
    app.run(debug=True)