# Generated by Django 5.1.3 on 2024-12-02 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('join_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='conform_password',
            new_name='confirm_password',
        ),
        migrations.AddField(
            model_name='user',
            name='color',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='emblem',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]