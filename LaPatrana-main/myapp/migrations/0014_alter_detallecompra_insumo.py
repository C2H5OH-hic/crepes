# Generated by Django 5.0.3 on 2024-12-28 00:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_insumo_remove_detallecompra_descripcion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detallecompra',
            name='insumo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.insumo'),
        ),
    ]
