# Generated by Django 3.1.3 on 2020-11-24 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20201119_0244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movementlist',
            name='list_type',
            field=models.CharField(choices=[('ARR', 'Заезд'), ('LVN', 'Выезд')], default='ARR', max_length=3, verbose_name='Тип списка'),
        ),
    ]