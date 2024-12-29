# Generated by Django 5.0.3 on 2024-12-27 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_actividad_ingrediente_alter_producto_descripcion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingrediente',
            name='unidad_medida',
            field=models.CharField(choices=[('kg', 'Kilogramo'), ('litro', 'Litro'), ('unidad', 'Unidad')], default='kg', max_length=20),
        ),
        migrations.AlterField(
            model_name='producto',
            name='descripcion',
            field=models.CharField(blank=True, max_length=450, null=True),
        ),
    ]