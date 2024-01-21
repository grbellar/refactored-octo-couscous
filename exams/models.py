from django.db import models
from django.conf import settings


class Exam(models.Model):
    name = models.CharField(max_length=300)
    question = models.ManyToManyField('Question')


    def __str__(self):
        return f'{self.name}'



class Question(models.Model):
    question = models.TextField(null=False, blank=False)


    def __str__(self):
        return f'Question {self.id}'


    class Meta:
        ordering = ["id"]


class Choice(models.Model):
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="choices")
    text = models.TextField(null=False, blank=False)
    is_correct = models.BooleanField()


class UserExamState(models.Model):
    exam = models.ForeignKey('Exam', on_delete=models.DO_NOTHING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    current_question_index = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)


    class Meta:
        unique_together = ('user', 'exam')  # Ensure one entry per user per exam


class UserExamAnswer(models.Model):
    user_exam_state = models.ForeignKey(UserExamState, on_delete=models.DO_NOTHING)


#TODO: 1. Add UserExamAnswers so I can store answer and grade them at the end. https://chat.openai.com/c/c97dd7b4-9f20-4ba7-a180-7d9ae684d04b
    # Link has an example of a 'through' model which I think would work quite well in this instance.
    # 2. Build grading functionality and test