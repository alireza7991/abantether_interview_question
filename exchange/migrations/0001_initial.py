# Generated by Django 5.1.3 on 2024-11-15 15:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
                ('code', models.CharField(db_index=True, max_length=16, unique=True, verbose_name='Code')),
                ('price_usd', models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Price')),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=12, max_digits=20, verbose_name='Amount')),
                ('state', models.CharField(choices=[('P', 'Pending'), ('D', 'Done'), ('C', 'Canceled'), ('F', 'Failed')], default='P', max_length=1, verbose_name='State')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='exchange.currency', verbose_name='Currency')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]
