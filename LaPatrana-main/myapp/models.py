from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint
from django.conf import settings
from decimal import Decimal

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
        Si no hay ingredientes o actividades, devuelve 0.
        """
        try:
            return self.costo_ingredientes() + self.costo_actividades()
        except Exception as e:
            print(f"Error calculando el costo unitario: {e}")
            return 0

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
            "costo_unitario_iva": self.calcular_costo_unitario_con_iva(),
            "precio_venta": self.precio,
            "margen_beneficio": self.margen_beneficio(),
            "margen_beneficio_iva": self.margen_beneficio_con_iva(),
        }
        return costos

    def verificar_ingredientes_disponibles(self):
        """
        Verifica si todos los ingredientes están disponibles para producir el producto.
        Devuelve una lista de faltantes o "Todo está disponible".
        """
        ingredientes = ProductoIngrediente.objects.filter(producto=self)
        faltantes = []

        for ingrediente in ingredientes:
            if ingrediente.ingrediente.stock_actual < ingrediente.cantidad_requerida:
                faltantes.append(
                    f"Falta {ingrediente.cantidad_requerida - ingrediente.ingrediente.stock_actual} "
                    f"{ingrediente.ingrediente.unidad_medida} de {ingrediente.ingrediente.nombre}"
                )

        return faltantes or "Todo está disponible"

    def generar_reporte_costos(self):
        """
        Genera un reporte en formato JSON con los costos y márgenes del producto.
        """
        import json
        return json.dumps(self.analizar_costos(), indent=4)

    def __str__(self):
        return f"{self.nombre} - ${self.precio} CLP"

    def calcular_costo_unitario_con_iva(self):
        """
        Calcula el costo unitario total del producto sumando ingredientes y actividades,
        incluyendo el IVA.
        """
        costo_unitario = self.calcular_costo_unitario()
        return costo_unitario * (1 + settings.IVA_RATE)

    def margen_beneficio_con_iva(self):
        """
        Calcula el margen de beneficio considerando el costo con IVA.
        """
        return self.precio - self.calcular_costo_unitario_con_iva()

class Ingrediente(models.Model):
    CATEGORIAS = [
        ('base', 'Base'),          # Ingredientes básicos, como harina o leche.
        ('adicional', 'Adicional')  # Ingredientes adicionales, como frutas o toppings.
    ]
    
    nombre = models.CharField(max_length=50, unique=True)  # Nombre único del ingrediente.
    unidad_medida = models.CharField(                     # Unidad en la que se mide.
        max_length=20,
        choices=[
            ('kg', 'Kilogramo'),
            ('litro', 'Litro'),
            ('unidad', 'Unidad'),
        ],
        default='unidad'
    )
    costo_por_unidad = models.DecimalField(               # Costo promedio ponderado del ingrediente.
        max_digits=10,
        decimal_places=2,
        default=0.0,
        editable=False  # No se modifica directamente por el usuario.
    )
    stock_actual = models.DecimalField(                   # Cantidad actual en stock.
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    categoria = models.CharField(                         # Clasificación del ingrediente.
        max_length=20,
        choices=CATEGORIAS,
        default='adicional'
    )

    def actualizar_costo(self, cantidad_comprada, precio_unitario):
        """
        Actualiza el costo promedio ponderado y el stock actual del ingrediente.
        """
        if cantidad_comprada <= 0 or precio_unitario <= 0:
            raise ValueError("Cantidad comprada y precio unitario deben ser mayores que cero.")

        nuevo_stock = self.stock_actual + cantidad_comprada
        self.costo_por_unidad = (
            (self.stock_actual * self.costo_por_unidad + cantidad_comprada * precio_unitario) / nuevo_stock
        )
        self.stock_actual = nuevo_stock
        self.save()

        # Registrar historial de costos (opcional)
        HistorialCostoIngrediente.objects.create(
            ingrediente=self,
            costo_por_unidad=self.costo_por_unidad
        )

    def tiene_stock_suficiente(self, cantidad_requerida):
        """
        Verifica si hay suficiente stock disponible para una cantidad requerida.
        """
        return self.stock_actual >= cantidad_requerida

    def __str__(self):
        return self.nombre


class HistorialCostoIngrediente(models.Model):
    """
    Registra un historial de los costos por unidad de un ingrediente.
    """
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name='historial_costos')
    costo_por_unidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ingrediente.nombre} - ${self.costo_por_unidad} el {self.fecha}"

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

    def necesita_reabastecimiento(self, minimo=1):
        """
        Verifica si el stock actual está por debajo de un nivel mínimo.
        """
        return self.stock_actual <= Decimal(minimo)

    def __str__(self):
        return self.nombre


# Relación Producto-Ingreditente

class ProductoIngrediente(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad_requerida = models.DecimalField(max_digits=10, decimal_places=2)  # Cantidad necesaria por unidad

    class Meta:
        constraints = [
            UniqueConstraint(fields=['producto', 'ingrediente'], name='unique_producto_ingrediente')
        ]

    def __str__(self):
        return f"{self.cantidad_requerida} {self.ingrediente.unidad_medida} de {self.ingrediente.nombre} para {self.producto.nombre}"

# Modelo de Actividades
class Actividad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    unidades_producidas = models.PositiveIntegerField(default=0)  # Total de productos vinculados a esta actividad

    def costo_por_unidad(self):
        """
        Calcula el costo por unidad basado en las unidades producidas.
        """
        if self.unidades_producidas > 0:
            return self.costo_total / self.unidades_producidas
        return 0.0

    def registrar_produccion(self, unidades):
        """
        Incrementa el número de unidades producidas.
        """
        self.unidades_producidas += unidades
        self.save()

    def actualizar_costo_total(self, nuevo_costo):
        """
        Actualiza el costo total de la actividad y recalcula automáticamente el costo por unidad.
        """
        self.costo_total = nuevo_costo
        self.save()

    def __str__(self):
        return f"{self.nombre} - {self.costo_total} CLP"

# Relación Producto-Actividad (Pesos)
class ProductoActividad(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)

    def costo_actividad(self):
        """
        Calcula el costo proporcional de la actividad basado en el peso asignado al producto.
        """
        return self.actividad.costo_por_unidad() * self.peso

    def save(self, *args, **kwargs):
        """
        Validación adicional para asegurar que el peso sea mayor a 0.
        """
        if self.peso <= 0:
            raise ValidationError("El peso debe ser mayor a 0.")
        super().save(*args, **kwargs)

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
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
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

    def save(self, *args, **kwargs):
        """
        Reduce el stock de los ingredientes necesarios al guardar el pedido.
        """
        super().save(*args, **kwargs)  # Guarda el pedido
        # Reducir el stock de ingredientes utilizados
        ingredientes = ProductoIngrediente.objects.filter(producto=self.producto)
        for ingrediente in ingredientes:
            ingrediente.ingrediente.stock_actual -= ingrediente.cantidad_requerida * self.cantidad
            if ingrediente.ingrediente.stock_actual < 0:
                raise ValidationError(f"Stock insuficiente para {ingrediente.ingrediente.nombre}.")
            ingrediente.ingrediente.save()

    def __str__(self):
        return f"Detalle del Pedido {self.pedido.idPedido} - {self.producto.nombre}"

# Modelo de Factura
class Compra(models.Model):
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Compra de {self.proveedor.nombre} el {self.fecha}"

from django.core.exceptions import ValidationError
from django.db import models


class DetalleCompra(models.Model):
    TIPO_CHOICES = [
        ('ingrediente', 'Ingrediente'),
        ('insumo', 'Insumo'),
    ]

    compra = models.ForeignKey('Compra', on_delete=models.CASCADE, related_name='detalles')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    ingrediente = models.ForeignKey('Ingrediente', on_delete=models.CASCADE, null=True, blank=True)
    nombre_insumo = models.CharField(max_length=100, null=True, blank=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        """
        Validaciones para asegurar que los datos coincidan con el tipo seleccionado.
        """
        if self.tipo == 'ingrediente' and not self.ingrediente:
            raise ValidationError("Debe seleccionar un ingrediente si el tipo es 'ingrediente'.")
        if self.tipo == 'insumo' and not self.nombre_insumo:
            raise ValidationError("Debe ingresar el nombre del insumo si el tipo es 'insumo'.")
        if not self.tipo:
            raise ValidationError("El campo tipo es obligatorio.")
        super().clean()

    def save(self, *args, **kwargs):
        """
        Actualiza automáticamente el stock de ingredientes o insumos al guardar una compra.
        """
        super().save(*args, **kwargs)  # Guarda el detalle de compra
        if self.tipo == 'ingrediente' and self.ingrediente:
            # Actualizar stock y costo del ingrediente
            self.ingrediente.actualizar_costo(Decimal(self.cantidad), Decimal(self.precio_unitario))
        elif self.tipo == 'insumo' and self.nombre_insumo:
            # Actualizar stock del insumo
            insumo, created = Insumo.objects.get_or_create(nombre=self.nombre_insumo)
            insumo.stock_actual += self.cantidad
            insumo.save()

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    razon_social = models.CharField(max_length=255, blank=True, null=True)
    rut = models.CharField(max_length=20, blank=True, null=True)
    actividad = models.CharField(max_length=255, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    contacto = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre

