# Generated by Django 5.1.3 on 2024-11-13 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_question_tags_answer'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='questionlike',
            index=models.Index(fields=['user', 'question'], name='app_questio_user_id_a178c0_idx'),
        ),
    ]