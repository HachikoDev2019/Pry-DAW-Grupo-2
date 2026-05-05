from flask import Flask, render_template, request
from requerimientoAD import clsRequerimiento, insertar_requerimiento

app = Flask(__name__)

@app.route("/")
def inicio():
    # Renderiza el wireframe del formulario
    return render_template("form_requerimiento.html")

@app.route("/guardar_requerimiento", methods=["POST"])
def guardar_requerimiento():
    try:
        # Se captura la data del formulario
        objRequerimiento = clsRequerimiento(
            request.form["titulo"], 
            request.form["area"], 
            request.form["fecha_limite"], 
            request.form["descripcion"]
        )
        
        # Se intenta insertar en la BD
        if insertar_requerimiento(objRequerimiento):
            return "Requerimiento publicado correctamente en el portal de Pomalca."
        return "Error al registrar el requerimiento."
    except Exception as e:
        return "Excepción capturada: " + repr(e)

if __name__ == "__main__":
    app.run(debug=True)