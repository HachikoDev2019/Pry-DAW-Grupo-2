from flask import Flask, render_template, request
from maquinariaAD import clsMaquinaria, insertar_maquinaria

app = Flask(__name__)

@app.route("/registro_maquinaria")
def registro_maquinaria():
    # Renderiza la vista que armamos con tu diseño
    return render_template("form_maquinaria.html")

@app.route("/guardar_maquinaria", methods=["POST"])
def guardar_maquinaria():
    try:
        objMaquinaria = clsMaquinaria(
            request.form["nombre_codigo"],
            request.form["tipo"],
            request.form["marca"],
            request.form["modelo"],
            request.form["area"],
            request.form["estado"],
            request.form["observaciones"]
        )
        if insertar_maquinaria(objMaquinaria):
            return "Maquinaria registrada correctamente en el sistema Pomalca."
        return "Error al registrar la maquinaria."
    except Exception as e:
        return "Excepción capturada: " + repr(e)

if __name__ == "__main__":
    app.run(debug=True)
