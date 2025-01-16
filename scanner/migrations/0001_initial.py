# Generated by Django 5.1.4 on 2025-01-16 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode', models.CharField(max_length=13, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('category', models.CharField(blank=True, max_length=200, null=True)),
                ('brand', models.CharField(blank=True, max_length=200, null=True)),
                ('image_url', models.URLField(blank=True, null=True)),
                ('recycling_type', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=255, unique=True)),
                ('score', models.IntegerField(default=0)),
            ],
        ),
    ]
