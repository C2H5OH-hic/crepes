# Generated by Django 5.0.3 on 2024-11-13 00:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_pedido_estado_alter_pedido_mesa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='estado',
            field=models.CharField(default='pendiente', max_length=20),
        ),
        migrations.AlterField(
            model_name='pedido',
            name='mesa',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.mesa'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pedido',
            name='numeroPedido',
            field=models.IntegerField(default=1),
        ),
    ]