# Generated by Django 5.1.3 on 2024-11-12 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0007_alter_cadastrotecnicofederal_validade_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='InfoRota',
        ),
        migrations.AddField(
            model_name='fornecedormateriaprima',
            name='distancia',
            field=models.IntegerField(blank=True, null=True, verbose_name='Distância em Metros'),
        ),
    ]