import os
from datetime import datetime
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from models.database import obtener_config_comercio
from utils.rutas import ruta_carpeta_comprobantes

def generar_ticket_pdf(id_operacion: int, items_carrito: list, total: float, usuario: str) -> str:
    """
    Genera un comprobante en formato ticket térmico (80mm de ancho).
    """
    carpeta_dest = ruta_carpeta_comprobantes()
    fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = os.path.join(carpeta_dest, f"Ticket_{id_operacion}_{fecha_str}.pdf")

    # Dimensiones estándar POS: 80 mm de ancho
    # Altura dinámica base: 130 mm + 10 mm extra por cada producto agregado
    ancho_ticket = 80 * mm
    alto_ticket = (130 + (len(items_carrito) * 10)) * mm

    doc = SimpleDocTemplate(
        nombre_archivo,
        pagesize=(ancho_ticket, alto_ticket),
        rightMargin=4 * mm,
        leftMargin=4 * mm,
        topMargin=8 * mm,
        bottomMargin=8 * mm
    )

    story = []
    styles = getSampleStyleSheet()

    # Estilos tipográficos compactos
    estilo_centro_bold = ParagraphStyle(
        'CentroBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        alignment=1
    )
    estilo_info = ParagraphStyle(
        'InfoTicket',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=1,
        textColor=colors.HexColor("#333333")
    )
    estilo_desc = ParagraphStyle(
        'DescProd',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9
    )

    cfg = obtener_config_comercio()

    # Cabecera dinámica del comercio
    story.append(Paragraph(cfg["nombre"], estilo_centro_bold))
    if cfg["direccion"]:
        story.append(Paragraph(cfg["direccion"], estilo_info))
    if cfg["telefono"]:
        story.append(Paragraph(f"Tel: {cfg['telefono']}", estilo_info))
    if cfg["cuit"]:
        story.append(Paragraph(f"CUIT/RUT: {cfg['cuit']}", estilo_info))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("DOCUMENTO NO FISCAL", estilo_info))
    story.append(Paragraph("TICKET DE VENTA", estilo_info))

    # Tabla de artículos (ancho útil: ~72mm)
    # Columnas: Cant (10mm) | Producto (38mm) | Subtotal (24mm)
    datos_tabla = [["Cant", "Detalle", "Subtotal"]]
    for item in items_carrito:
        p_desc = Paragraph(item['nombre'], estilo_desc)
        datos_tabla.append([
            str(item['cantidad']),
            p_desc,
            f"${item['subtotal']:,.2f}"
        ])

    # Fila de Cierre / Total
    datos_tabla.append(["", "TOTAL:", f"${total:,.2f}"])

    tabla = Table(datos_tabla, colWidths=[10 * mm, 38 * mm, 24 * mm])
    tabla.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),      # Separador cabecera
        ('LINEABOVE', (0, -1), (-1, -1), 0.8, colors.black),    # Línea sobre el total
        ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (1, -1), (-1, -1), 9),
    ]))

    story.append(tabla)
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(cfg["leyenda"] or "¡Gracias por su compra!", estilo_info))

    doc.build(story)
    return os.path.abspath(nombre_archivo)