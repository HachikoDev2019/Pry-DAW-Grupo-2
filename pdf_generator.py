import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generar_pdf_solicitud(
        id_solicitud,
        trabajador,
        descripcion,
        area,
        prioridad):

    carpeta = "static/documentos/solicitudes"

    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    nombre_archivo = f"solicitud_{id_solicitud}.pdf"

    ruta_pdf = os.path.join(carpeta, nombre_archivo)

    pdf = canvas.Canvas(ruta_pdf, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(180, 760, "SOLICITUD DE REQUERIMIENTO")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(50, 700, f"ID: {id_solicitud}")
    pdf.drawString(50, 670, f"Trabajador: {trabajador}")
    pdf.drawString(50, 640, f"Área: {area}")
    pdf.drawString(50, 610, f"Prioridad: {prioridad}")

    pdf.drawString(50, 560, "Descripción:")

    texto = pdf.beginText(50, 530)
    texto.textLines(descripcion)
    pdf.drawText(texto)

    pdf.save()

    return ruta_pdf