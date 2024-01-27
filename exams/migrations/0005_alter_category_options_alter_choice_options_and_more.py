# Generated by Django 4.2.5 on 2024-01-27 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0004_alter_useranswer_question_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='choice',
            options={'verbose_name': 'Question Choice'},
        ),
        migrations.AlterModelOptions(
            name='userexamstate',
            options={'verbose_name': 'User Exam'},
        ),
        migrations.AlterField(
            model_name='exam',
            name='questions',
            field=models.ManyToManyField(blank=True, to='exams.question'),
        ),
    ]