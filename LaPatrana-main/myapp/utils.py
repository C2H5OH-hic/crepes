from django.core.mail import EmailMessage
from django.utils.timezone import now
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Pedido, Compra, DetallePedido

def enviar_informe_caja_diaria():
    fecha_actual = now().date()
    pedidos = Pedido.objects.filter(created_at__date=fecha_actual, estado='despachado')
    compras = Compra.objects.filter(fecha__date=fecha_actual)

    # Generar el PDF en memoria
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(f"Informe Caja Diaria - {fecha_actual}")
    
    ancho, alto = letter
    y = alto - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, y, f"Caja Diaria - {fecha_actual}")
    y -= 30

    total_caja = sum(sum(detalle.cantidad * detalle.producto.precio for detalle in DetallePedido.objects.filter(pedido=pedido)) for pedido in pedidos)
    total_compras = sum(sum(detalle.cantidad * detalle.precio_unitario for detalle in compra.detalles.all()) for compra in compras)
    
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Total de Ingresos: ${total_caja:.2f}")
    y -= 20
    pdf.drawString(50, y, f"Total de Compras: ${total_compras:.2f}")
    y -= 20
    pdf.drawString(50, y, f"Balance Neto: ${total_caja - total_compras:.2f}")
    y -= 40

    pdf.save()
    buffer.seek(0)

    # Preparar y enviar el correo
    email = EmailMessage(
        subject=f"Informe Caja Diaria - {fecha_actual}",
        body="Adjunto el informe diario de la caja.",
        from_email='ca.zunigavera@gmail.com',
        to=['ca.zunigavera@gmail.com'],  # Cambia esto por el correo de destino
    )
    email.attach(f"Caja_Diaria_{fecha_actual}.pdf", buffer.read(), "application/pdf")
    email.send()
