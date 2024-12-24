from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Ingrediente, ProductoIngrediente, Actividad, ProductoActividad, ValidacionCosto

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

# Formulario para asignar ingredientes a productos
class ProductoIngredienteForm(forms.ModelForm):
    class Meta:
        model = ProductoIngrediente
        fields = ['ingrediente', 'cantidad_requerida']  # Nota: Eliminamos "producto" porque el formset lo gestiona

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

# Formset para manejar múltiples ingredientes asociados a un producto
ProductoIngredienteFormSet = inlineformset_factory(
    Producto,
    ProductoIngrediente,
    fields=['ingrediente', 'cantidad_requerida'],
    extra=1,
    can_delete=True
)