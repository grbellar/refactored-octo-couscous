# Generated by Django 4.2.5 on 2024-01-21 19:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0010_auto_20240121_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
