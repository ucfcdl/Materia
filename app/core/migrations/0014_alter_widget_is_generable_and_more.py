# Generated by Django 5.0.1 on 2025-01-30 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_usersettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='widget',
            name='is_generable',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='widget',
            name='uses_prompt_generation',
            field=models.BooleanField(default=False),
        ),
    ]
