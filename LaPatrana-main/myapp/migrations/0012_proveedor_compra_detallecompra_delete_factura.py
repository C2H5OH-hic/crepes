# Generated by Django 5.0.3 on 2024-12-27 21:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_alter_ingrediente_unidad_medida_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('contacto', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.proveedor')),
            ],
        ),
        migrations.CreateModel(
            name='DetalleCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(blank=True, max_length=255, null=True)),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('es_ingrediente', models.BooleanField(default=False)),
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='myapp.compra')),
                ('ingrediente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.ingrediente')),
            ],
        ),
        migrations.DeleteModel(
            name='Factura',
        ),
    ]
