from flask import Flask, render_template, request, redirect, url_for, flash
from maquinariaAD import clsMaquinaria, insertar_maquinaria
from solicitudAD import clsSolicitud, insertar_solicitud, listar_mis_solicitudes

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


if __name__ == "__main__":
    app.run(debug=True)