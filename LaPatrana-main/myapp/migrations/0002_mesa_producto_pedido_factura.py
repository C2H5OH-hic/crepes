# Generated by Django 5.0.3 on 2024-05-09 16:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mesa',
            fields=[
                ('idMesa', models.AutoField(primary_key=True, serialize=False)),
                ('numero', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('idProducto', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=100)),
                ('disponible', models.BooleanField(default=True)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nombre', models.CharField(default='', max_length=50)),
                ('imgProducto', models.ImageField(null=True, upload_to='myapp/static/img')),
            ],
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('idPedido', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.IntegerField()),
                ('hecho', models.BooleanField(default=False)),
                ('idMesero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('mesa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.mesa')),
                ('idProducto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.producto')),
            ],
        ),
        migrations.CreateModel(
            name='Factura',
            fields=[
                ('idFactura', models.AutoField(primary_key=True, serialize=False)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('hora', models.DateTimeField(auto_now_add=True)),
                ('idPedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.pedido')),
            ],
        ),
    ]
