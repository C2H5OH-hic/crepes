# Generated by Django 5.0.3 on 2024-11-13 01:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_remove_factura_mesa_remove_pedido_mesa_delete_mesa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedido',
            name='numeroPedido',
        ),
    ]
