# Generated by Django 5.1.4 on 2025-01-17 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_proxbox', '0004_fastapiendpoint_netboxendpoint_proxmoxendpoint_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proxmoxendpoint',
            name='name',
            field=models.CharField(blank=True, default='Proxmox Endpoint', max_length=255, null=True),
        ),
    ]
