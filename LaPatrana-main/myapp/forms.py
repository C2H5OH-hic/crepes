from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import Producto, Ingrediente, ProductoIngrediente, Actividad, ProductoActividad, ValidacionCosto, Compra, DetalleCompra, Proveedor

# Formulario para gestionar productos
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'disponible', 'imgProducto']

# Formulario para gestionar ingredientes
class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ['nombre', 'unidad_medida', 'costo_por_unidad', 'stock_actual']
        widgets = {
            'unidad_medida': forms.Select(choices=[
                ('kg', 'Kilogramo'),
                ('litro', 'Litro'),
                ('unidad', 'Unidad'),
            ]),
        }

# Formulario para gestionar actividades
class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['nombre', 'descripcion', 'costo_total', 'unidades_producidas']

# Formulario para asignar actividades a productos
class ProductoActividadForm(forms.ModelForm):
    class Meta:
        model = ProductoActividad
        fields = ['producto', 'actividad', 'peso']

# Formulario para validar costos
class ValidacionCostoForm(forms.ModelForm):
    class Meta:
        model = ValidacionCosto
        fields = ['producto', 'cantidad_producida', 'costo_real']

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor']

# Formulario para Crear Ingredientes (si se necesita por separado)
class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ['nombre', 'unidad_medida', 'costo_por_unidad', 'stock_actual']

ProductoIngredienteFormSet = inlineformset_factory(
    Producto,
    ProductoIngrediente,
    fields=['ingrediente', 'cantidad_requerida'],
    extra=1,  # Número de formularios adicionales iniciales
    can_delete=True  # Permitir eliminar formularios existentes
)

class DetalleCompraForm(forms.ModelForm):
    OPCIONES_TIPO = [
        ('ingrediente', 'Ingrediente'),
        ('insumo', 'Insumo'),
    ]

    tipo = forms.ChoiceField(choices=OPCIONES_TIPO, widget=forms.RadioSelect, label="Tipo")
    ingrediente = forms.ModelChoiceField(
        queryset=Ingrediente.objects.all(),
        required=False,
        label="Ingrediente"
    )
    nombre_insumo = forms.CharField(
        required=False,
        label="Insumo",
        widget=forms.TextInput(attrs={'placeholder': 'Escribe el nombre del insumo'})
    )

    class Meta:
        model = DetalleCompra
        fields = ['tipo', 'ingrediente', 'nombre_insumo', 'cantidad', 'precio_unitario']

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto', 'direccion']

DetalleCompraFormSet = modelformset_factory(
    DetalleCompra,
    form=DetalleCompraForm,
    extra=1,
    can_delete=True
)