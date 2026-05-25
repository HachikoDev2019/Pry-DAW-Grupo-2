from flask import Flask, render_template, request, redirect, url_for, flash
from maquinariaAD import clsMaquinaria, insertar_maquinaria

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
        if insertar_maquinaria(objMaquinaria):
             return render_template("maquinaria.html")
            
        return "Error al registrar la maquinaria."
    except Exception as e:
        flash(f"Error inesperado: {repr(e)}", "error")
        return redirect(url_for("registro_maquinaria"))


if __name__ == "__main__":
    app.run(debug=True)