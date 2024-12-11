from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class User(AbstractUser):
    # Tus propiedades personalizadas
    is_chef = models.BooleanField(default=False)
    is_cashier = models.BooleanField(default=False)


class Producto(models.Model):
    idProducto = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    disponible = models.BooleanField(default=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    nombre = models.CharField(max_length=50, default="")
    imgProducto = models.ImageField(upload_to="myapp/static/img", null=True)

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    # Opciones de estado del pedido
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('listo', 'Listo'),
        ('despachado', 'Despachado'),
    ]

    idPedido = models.AutoField(primary_key=True)
    idCajero = models.ForeignKey(User, on_delete=models.CASCADE)
    cliente_nombre = models.CharField(max_length=100, default="Cliente")
    productos = models.ManyToManyField(Producto, through='DetallePedido')
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='pendiente'
    )  # Campo con estados definidos por choices
    
    created_at = models.DateTimeField(default=now)
    
    def __str__(self):
        return f"Pedido {self.idPedido} - {self.get_estado_display()}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('listo', 'Listo'),
        ],
        default='pendiente'
    )

    def __str__(self):
        return f"Detalle del Pedido {self.pedido.idPedido} - {self.producto.nombre}"

class Factura(models.Model):
    idFactura = models.AutoField(primary_key=True)
    valor = models.DecimalField(max_digits=20, decimal_places=2)
    hora = models.DateTimeField(null=True)
    fecha = models.DateField(null=True)
    cosasPedidas = models.CharField(max_length=400)
    idCajero = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Factura {self.idFactura} - {self.valor}"