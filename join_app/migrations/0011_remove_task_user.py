# Generated by Django 5.1.3 on 2024-12-17 19:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('join_app', '0010_remove_usercontact_contact_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='user',
        ),
    ]