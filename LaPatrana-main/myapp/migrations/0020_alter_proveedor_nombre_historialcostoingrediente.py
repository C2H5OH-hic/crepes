# Generated by Django 5.1.4 on 2025-01-02 08:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_proveedor_actividad_proveedor_ciudad_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proveedor',
            name='nombre',
            field=models.CharField(max_length=100),
        ),
        migrations.CreateModel(
            name='HistorialCostoIngrediente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('costo_por_unidad', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('ingrediente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial_costos', to='myapp.ingrediente')),
            ],
        ),
    ]
