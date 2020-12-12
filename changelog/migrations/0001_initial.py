# Generated by Django 3.1.3 on 2020-12-12 16:16

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_datetime', models.DateTimeField(verbose_name='Дата и время изменения')),
                ('action', models.CharField(choices=[('CREATE', 'Создание'), ('UPDATE', 'Изменение'), ('DELETE', 'Удаление'), ('RESTORE', 'Восстановление')], max_length=10, verbose_name='Тип изменения')),
                ('model', models.CharField(max_length=255, verbose_name='Имя модели изменяемого объекта')),
                ('model_pk', models.IntegerField(verbose_name='Первичный ключ изменяемого объекта')),
                ('prev_change', models.JSONField(blank=True, null=True, verbose_name='Данные до изменения в формате JSON')),
                ('post_change', models.JSONField(blank=True, null=True, verbose_name='Измененные данные в формате JSON')),
                ('comment', models.TextField(blank=True, default='', verbose_name='Текстовый комментарий')),
                ('changed_by', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Кем изменено')),
            ],
            options={
                'verbose_name': 'Историческая запись',
                'verbose_name_plural': 'Исторические записи',
                'ordering': ('change_datetime',),
            },
        ),
    ]
