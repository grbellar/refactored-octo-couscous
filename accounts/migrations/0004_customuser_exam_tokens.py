# Generated by Django 4.2.5 on 2024-02-10 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_customuser_school'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='exam_tokens',
            field=models.IntegerField(default=0),
        ),
    ]