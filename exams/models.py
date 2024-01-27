import uuid
from django.db import models
from django.conf import settings

# TODO: 1. Maybe use UUID to uniquely identify each question. 

class ExamType(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return f'{self.name}'


class Exam(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # Using this for url parameters
    name = models.CharField(max_length=300)
    questions = models.ManyToManyField('Question')
    exam_type = models.ForeignKey("ExamType", on_delete=models.SET_NULL, related_name="exams", null=True)

    def __str__(self):
        return f'{self.name}'


class Category(models.Model):
    name = models.CharField(max_length=300)
    exam_type = models.ForeignKey("ExamType", on_delete=models.SET_NULL, related_name="categories", null=True)

    def __str__(self):
        return f'{self.name}'


class Question(models.Model):
    text = models.TextField(null=False, blank=False)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, related_name="questions", null=True)

    def __str__(self):
        return f'Question {self.id}'

    class Meta:
        ordering = ["id"]


class Choice(models.Model):
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="choices")
    text = models.TextField(null=False, blank=False)
    is_correct = models.BooleanField()

    def __str__(self):
        return f'{self.text}'


class UserExamState(models.Model):
    exam = models.ForeignKey('Exam', on_delete=models.DO_NOTHING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    current_question_index = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    answers = models.ManyToManyField('Question', through='UserAnswer') #TODO: I maybe don't need this relationship
                                                                        # but probably best to leave just in case, see
                                                                        # https://chat.openai.com/c/4150bbd8-7b7d-43c8-8fb1-b9a710df4c4f

    def grade():
        # TODO: Build grading functionality and test
        # Something like for all answers in state... check right or wrong.
        pass

    class Meta:
        unique_together = ('user', 'exam')  # Ensure one entry per user per exam


class UserAnswer(models.Model):
    user_exam_state = models.ForeignKey(UserExamState, on_delete=models.DO_NOTHING, related_name="user_answers")
    question = models.ForeignKey('Question', default=None, on_delete=models.DO_NOTHING)
    selected_choice = models.ForeignKey('Choice', default=None, on_delete=models.DO_NOTHING)
