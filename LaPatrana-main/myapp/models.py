from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.core.exceptions import ValidationError

# Usuario personalizado
class User(AbstractUser):
    is_chef = models.BooleanField(default=False)
    is_cashier = models.BooleanField(default=False)


# Modelo de Producto
class Producto(models.Model):
    idProducto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=450, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio de venta al público
    disponible = models.BooleanField(default=True)  # Indica si está disponible para la venta
    imgProducto = models.ImageField(upload_to="img", blank=True, null=True)  # Imagen opcional del producto

    def calcular_costo_unitario(self):
        """
        Calcula el costo unitario total del producto sumando ingredientes y actividades.
        """
        return self.costo_ingredientes() + self.costo_actividades()

    def margen_beneficio(self):
        """
        Calcula el margen de beneficio del producto:
        Margen = Precio de venta - Costo unitario.
        """
        return self.precio - self.calcular_costo_unitario()

    def costo_ingredientes(self):
        """
        Calcula el costo total de los ingredientes vinculados al producto.
        """
        ingredientes = ProductoIngrediente.objects.filter(producto=self)
        return sum(i.cantidad_requerida * i.ingrediente.costo_por_unidad for i in ingredientes) or 0

    def costo_actividades(self):
        """
        Calcula el costo total de las actividades vinculadas al producto.
        """
        actividades = ProductoActividad.objects.filter(producto=self)
        return sum(a.costo_actividad() for a in actividades) or 0

    def analizar_costos(self):
        """
        Devuelve un desglose completo de los costos y márgenes del producto.
        """
        costos = {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "costo_ingredientes": self.costo_ingredientes(),
            "costo_actividades": self.costo_actividades(),
            "costo_unitario": self.calcular_costo_unitario(),
            "precio_venta": self.precio,
            "margen_beneficio": self.margen_beneficio(),
        }
        return costos

    def __str__(self):
        return f"{self.nombre} - ${self.precio} CLP"



class Ingrediente(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    unidad_medida = models.CharField(
        max_length=20,
        choices=[
            ('kg', 'Kilogramo'),
            ('litro', 'Litro'),
            ('unidad', 'Unidad'),
        ],
        default='unidad'
    )
    costo_por_unidad = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.nombre


class Insumo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    unidad_medida = models.CharField(
        max_length=20,
        choices=[
            ('unidad', 'Unidad'),
        ],
        default='unidad'
    )
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.nombre


# Relación Producto-Ingreditente
class ProductoIngrediente(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad_requerida = models.DecimalField(max_digits=10, decimal_places=2)  # Cantidad necesaria por unidad

    def __str__(self):
        return f"{self.cantidad_requerida} {self.ingrediente.unidad_medida} de {self.ingrediente.nombre} para {self.producto.nombre}"


# Modelo de Actividades
class Actividad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    unidades_producidas = models.PositiveIntegerField(default=0)  # Total de productos vinculados a esta actividad

    def costo_por_unidad(self):
        if self.unidades_producidas > 0:
            return self.costo_total / self.unidades_producidas
        return 0.0

    def registrar_produccion(self, unidades):
        # Incrementa el número de unidades producidas
        self.unidades_producidas += unidades
        self.save()

    def __str__(self):
        return f"{self.nombre} - {self.costo_total} CLP"


# Relación Producto-Actividad (Pesos)
class ProductoActividad(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)

    def costo_actividad(self):
        return self.actividad.costo_por_unidad() * self.peso

    def __str__(self):
        return f"{self.producto.nombre} - {self.actividad.nombre} (Peso: {self.peso})"


# Modelo de Validación de Costos
class ValidacionCosto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_producida = models.PositiveIntegerField()
    costo_calculado = models.DecimalField(max_digits=10, decimal_places=2)
    costo_real = models.DecimalField(max_digits=10, decimal_places=2)
    discrepancia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.discrepancia = self.costo_real - self.costo_calculado
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Validación {self.producto.nombre} - Diferencia: {self.discrepancia} CLP"


# Modelo de Pedido y DetallePedido (ya existente)
class Pedido(models.Model):
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
    )
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
    nota = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Detalle del Pedido {self.pedido.idPedido} - {self.producto.nombre}"


# Modelo de Factura
class Compra(models.Model):
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Compra de {self.proveedor.nombre} el {self.fecha}"

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    contacto = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre

class DetalleCompra(models.Model):
    compra = models.ForeignKey('Compra', on_delete=models.CASCADE, related_name='detalles')
    ingrediente = models.ForeignKey('Ingrediente', on_delete=models.CASCADE, null=True, blank=True)
    nombre_insumo = models.CharField(max_length=100, null=True, blank=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre_insumo or (self.ingrediente.nombre if self.ingrediente else "Sin Nombre")
