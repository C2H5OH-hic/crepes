from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
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
    pdf = canvas.Canvas(buffer, pagesize=letter)
    ancho, alto = letter
    y = alto - 50

    # Encabezado con logo y título
    logo_path = Path(settings.BASE_DIR).resolve() / 'myapp' / 'static' / 'img' / 'logocrepes.jpg'
    if logo_path.exists():
        pdf.drawImage(str(logo_path), 50, alto - 100, width=100, height=50)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(200, alto - 70, "Reporte Diario - Caja")
    pdf.line(50, alto - 120, ancho - 50, alto - 120)
    y = alto - 130

    # Calcular totales
    total_caja = sum(
        sum(detalle.cantidad * detalle.producto.precio for detalle in DetallePedido.objects.filter(pedido=pedido))
        for pedido in pedidos
    )
    total_compras = sum(
        sum(detalle.cantidad * detalle.precio_unitario for detalle in compra.detalles.all())
        for compra in compras
    )

    # Totales generales
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Total de Ingresos: ${total_caja:.2f}")
    pdf.drawString(50, y - 20, f"Total de Compras: ${total_compras:.2f}")
    pdf.drawString(50, y - 40, f"Balance Neto: ${total_caja - total_compras:.2f}")
    pdf.line(50, y - 50, ancho - 50, y - 50)
    y -= 70

    # Datos de pedidos
    detalles_pedidos = [
        [pedido.idPedido, pedido.cliente_nombre, pedido.created_at.strftime('%H:%M:%S'),
         "\n".join([f"{detalle.producto.nombre} (x{detalle.cantidad})" for detalle in DetallePedido.objects.filter(pedido=pedido)]),
         f"${sum(detalle.cantidad * detalle.producto.precio for detalle in DetallePedido.objects.filter(pedido=pedido)):.2f}"]
        for pedido in pedidos
    ]

    # Datos de compras
    detalles_compras = [
        [compra.id, compra.proveedor.nombre, compra.fecha.strftime('%H:%M:%S'),
         "\n".join([f"{detalle.nombre_insumo if detalle.nombre_insumo else detalle.ingrediente.nombre} - {detalle.cantidad} x ${detalle.precio_unitario:.2f}" for detalle in compra.detalles.all()]),
         f"${sum(detalle.cantidad * detalle.precio_unitario for detalle in compra.detalles.all()):.2f}"]
        for compra in compras
    ]

    # Tablas
    data_pedidos = [["ID Pedido", "Cliente", "Hora", "Productos", "Total"]] + detalles_pedidos
    data_compras = [["ID Compra", "Proveedor", "Hora", "Detalles", "Total"]] + detalles_compras

    table_pedidos = Table(data_pedidos, colWidths=[50, 100, 80, 250, 70])
    table_pedidos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    table_pedidos.wrapOn(pdf, 50, y - len(data_pedidos) * 20)
    table_pedidos.drawOn(pdf, 50, y - len(data_pedidos) * 20)

    y -= len(data_pedidos) * 20 + 40
    table_compras = Table(data_compras, colWidths=[50, 100, 80, 250, 70])
    table_compras.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    table_compras.wrapOn(pdf, 50, y - len(data_compras) * 20)
    table_compras.drawOn(pdf, 50, y - len(data_compras) * 20)

    pdf.save()
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
