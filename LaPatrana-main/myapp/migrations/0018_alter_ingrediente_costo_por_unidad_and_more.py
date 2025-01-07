# Generated by Django 5.1.4 on 2024-12-31 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_ingrediente_categoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingrediente',
            name='costo_por_unidad',
            field=models.DecimalField(decimal_places=2, default=0.0, editable=False, max_digits=10),
        ),
        migrations.AddConstraint(
            model_name='productoingrediente',
            constraint=models.UniqueConstraint(fields=('producto', 'ingrediente'), name='unique_producto_ingrediente'),
        ),
    ]
