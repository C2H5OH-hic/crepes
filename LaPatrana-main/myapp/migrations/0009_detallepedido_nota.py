# Generated by Django 5.0.3 on 2024-12-13 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_pedido_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='detallepedido',
            name='nota',
            field=models.TextField(blank=True, null=True),
        ),
    ]
