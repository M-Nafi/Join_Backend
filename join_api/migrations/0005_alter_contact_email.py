# Generated by Django 5.1.3 on 2024-12-06 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('join_api', '0004_create_guest_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]