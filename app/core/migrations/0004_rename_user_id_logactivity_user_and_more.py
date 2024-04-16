# Generated by Django 5.0.1 on 2024-04-11 19:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_delete_migration_delete_permroletoperm_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='logactivity',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='logplay',
            old_name='inst_id',
            new_name='instance',
        ),
        migrations.RenameField(
            model_name='logplay',
            old_name='qset_id',
            new_name='qset',
        ),
        migrations.RenameField(
            model_name='logplay',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='logstorage',
            old_name='inst_id',
            new_name='instance',
        ),
        migrations.RenameField(
            model_name='logstorage',
            old_name='play_id',
            new_name='play_log',
        ),
        migrations.RenameField(
            model_name='logstorage',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='lti',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='lti',
            old_name='item_id',
            new_name='widget_instance',
        ),
        migrations.RenameField(
            model_name='mapquestiontoqset',
            old_name='qset_id',
            new_name='qset',
        ),
        migrations.RenameField(
            model_name='mapquestiontoqset',
            old_name='question_id',
            new_name='question',
        ),
        migrations.RenameField(
            model_name='permobjecttouser',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='widgetinstance',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='widgetinstance',
            old_name='widget_id',
            new_name='widget',
        ),
        migrations.RenameField(
            model_name='widgetmetadata',
            old_name='widget_id',
            new_name='widget',
        ),
        migrations.RenameField(
            model_name='widgetqset',
            old_name='inst_id',
            new_name='instance',
        ),
    ]