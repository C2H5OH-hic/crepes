# Generated by Django 5.0.3 on 2024-11-13 00:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_alter_pedido_estado_alter_pedido_mesa_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='factura',
            name='mesa',
        ),
        migrations.RemoveField(
            model_name='pedido',
            name='mesa',
        ),
        migrations.DeleteModel(
            name='Mesa',
        ),
    ]