# Generated by Django 5.1.3 on 2024-12-16 15:30

import user_auth_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth_app', '0003_alter_customuser_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(help_text='150 Zeichen oder weniger. Buchstaben, Zahlen, Leerzeichen und @/./+/-/_ erlaubt.', max_length=150, unique=True, validators=[user_auth_app.models.validate_username]),
        ),
    ]
