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
        # Excluir el campo 'costo_por_unidad' explícitamente
        fields = ['nombre', 'unidad_medida', 'stock_actual', 'categoria']

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
        # Excluir 'costo_por_unidad' porque no es editable
        fields = ['nombre', 'unidad_medida', 'stock_actual', 'categoria']


ProductoIngredienteFormSet = inlineformset_factory(
    Producto,
    ProductoIngrediente,
    fields=['ingrediente', 'cantidad_requerida'],
    extra=1,  # Número de formularios adicionales iniciales
    can_delete=True  # Permitir eliminar formularios existentes
)

from django import forms
from .models import DetalleCompra, Ingrediente

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
        label="Nombre del Insumo",
        widget=forms.TextInput(attrs={'placeholder': 'Escribe el nombre del insumo'})
    )

    class Meta:
        model = DetalleCompra
        fields = ['tipo', 'ingrediente', 'nombre_insumo', 'cantidad', 'precio_unitario']


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'razon_social', 'rut', 'actividad', 'pais', 'ciudad', 'correo', 'contacto', 'direccion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

DetalleCompraFormSet = modelformset_factory(
    DetalleCompra,
    form=DetalleCompraForm,
    extra=0,  # No generar formularios adicionales vacíos
    can_delete=True
)

