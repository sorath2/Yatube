# Generated by Django 2.2.16 on 2023-03-09 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20230309_1256'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='follow constraint',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('author', 'user'), name='unique_members'),
        ),
    ]