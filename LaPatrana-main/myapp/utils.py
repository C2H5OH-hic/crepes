from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.core.mail import EmailMessage
from django.utils.timezone import now
from django.conf import settings
from pathlib import Path
from .models import Pedido, Compra, DetallePedido

def generar_pdf_caja_diaria():
    fecha_actual = now().date()
    pedidos = Pedido.objects.filter(created_at__date=fecha_actual, estado='despachado')
    compras = Compra.objects.prefetch_related('detalles').filter(fecha__date=fecha_actual)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # **Agregar el logo como marca de agua**
    logo_path = Path(settings.BASE_DIR) / "myapp" / "static" / "img" / "logocrepes.jpg"
    
    def draw_watermark(canvas, doc):
        if logo_path.exists():
            width, height = letter
            # Dibuja la imagen en el centro de la página con transparencia
            canvas.setFillAlpha(0.1)  # Transparencia del 10%
            canvas.drawImage(str(logo_path), width / 4, height / 4, width=300, height=300, preserveAspectRatio=True, mask='auto')
            canvas.setFillAlpha(1)  # Restaurar opacidad normal

    # **Encabezado**
    elements.append(Paragraph("<b>Reporte Diario - Caja</b>", styles['Title']))
    elements.append(Spacer(1, 12))  # Espaciado

    # **Resumen General**
    total_caja = sum(
        sum(detalle.cantidad * detalle.producto.precio for detalle in DetallePedido.objects.filter(pedido=pedido))
        for pedido in pedidos
    )
    total_compras = sum(
        sum(detalle.cantidad * detalle.precio_unitario for detalle in compra.detalles.all())
        for compra in compras
    )

    balance_neto = total_caja - total_compras
    elements.append(Paragraph(f"<b>Total de Ingresos:</b> ${total_caja:.2f}", styles['Normal']))
    elements.append(Paragraph(f"<b>Total de Compras:</b> ${total_compras:.2f}", styles['Normal']))
    elements.append(Paragraph(f"<b>Balance Neto:</b> ${balance_neto:.2f}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # **Tabla de Pedidos**
    elements.append(Paragraph("<b>Resumen de Pedidos</b>", styles['Heading2']))
    elements.append(Spacer(1, 6))

    data_pedidos = [["ID Pedido", "Cliente", "Hora", "Productos", "Total"]] + [
        [
            pedido.idPedido,
            pedido.cliente_nombre,
            pedido.created_at.strftime('%H:%M:%S'),
            "\n".join([f"{detalle.producto.nombre} (x{detalle.cantidad})" for detalle in DetallePedido.objects.filter(pedido=pedido)]),
            f"${sum(detalle.cantidad * detalle.producto.precio for detalle in DetallePedido.objects.filter(pedido=pedido)):.2f}"
        ]
        for pedido in pedidos
    ]

    table_pedidos = Table(data_pedidos, colWidths=[50, 100, 80, 200, 70])
    table_pedidos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table_pedidos)
    elements.append(Spacer(1, 12))

    # **Tabla de Compras**
    elements.append(Paragraph("<b>Resumen de Compras</b>", styles['Heading2']))
    elements.append(Spacer(1, 6))

    data_compras = [["ID Compra", "Proveedor", "Hora", "Detalles", "Total"]] + [
        [
            compra.id,
            compra.proveedor.nombre,
            compra.fecha.strftime('%H:%M:%S'),
            "\n".join([f"{detalle.nombre_insumo if detalle.nombre_insumo else detalle.ingrediente.nombre} - {detalle.cantidad} x ${detalle.precio_unitario:.2f}" for detalle in compra.detalles.all()]),
            f"${sum(detalle.cantidad * detalle.precio_unitario for detalle in compra.detalles.all()):.2f}"
        ]
        for compra in compras
    ]

    table_compras = Table(data_compras, colWidths=[50, 100, 80, 200, 70])
    table_compras.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table_compras)
    elements.append(Spacer(1, 12))

    # **Generar el PDF con marca de agua**
    doc.build(elements, onFirstPage=draw_watermark, onLaterPages=draw_watermark)
    buffer.seek(0)
    return buffer


def enviar_informe_caja_diaria():
    buffer = generar_pdf_caja_diaria()

    email = EmailMessage(
        subject=f"Informe Caja Diaria - {now().date()}",
        body="Adjunto el informe diario de la caja.",
        from_email='ca.zunigavera@gmail.com',
        to=['ca.zunigavera@gmail.com', 'mazma53@gmail.com'],
    )
    email.attach(f"Caja_Diaria_{now().date()}.pdf", buffer.getvalue(), "application/pdf")
    email.send()
