# Generated by Django 5.0.3 on 2024-12-22 07:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_detallepedido_nota'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('costo_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('unidades_producidas', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Ingrediente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True)),
                ('unidad_medida', models.CharField(default='kg', max_length=20)),
                ('costo_por_unidad', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('stock_actual', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.AlterField(
            model_name='producto',
            name='descripcion',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='producto',
            name='imgProducto',
            field=models.ImageField(blank=True, null=True, upload_to='img'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='nombre',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.CreateModel(
            name='ProductoActividad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('peso', models.DecimalField(decimal_places=2, default=1.0, max_digits=5)),
                ('actividad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.actividad')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.producto')),
            ],
        ),
        migrations.CreateModel(
            name='ProductoIngrediente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_requerida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ingrediente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.ingrediente')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.producto')),
            ],
        ),
        migrations.CreateModel(
            name='ValidacionCosto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_producida', models.PositiveIntegerField()),
                ('costo_calculado', models.DecimalField(decimal_places=2, max_digits=10)),
                ('costo_real', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discrepancia', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.producto')),
            ],
        ),
    ]
