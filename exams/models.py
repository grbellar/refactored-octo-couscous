import uuid
from django.db import models
from django.conf import settings

# TODO: 1. Use a UUID for exam id instead of a single int.
#       2. Use a UUID to uniquely identify each question. 
#       3. Add a question integer field that is unique to the exam, but not unique amonst all quetions. 
#           This will allow easier determination of order of questions for each exam.
# https://chat.openai.com/c/9bf5d44a-93bb-45fb-8a64-4cd5d31519b6
# Probably add UUID for external url consumption but keep pk as id for internal database lookups


class Exam(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # going to use this for url parameters
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
    answers = models.ManyToManyField('Question', through='UserAnswer')


    def grade():
        # TODO: Build grading functionality and test
        # Something like for all answers in state... check right or wrong.
        pass

    
    class Meta:
        unique_together = ('user', 'exam')  # Ensure one entry per user per exam


class UserAnswer(models.Model):
    user_exam_state = models.ForeignKey(UserExamState, on_delete=models.DO_NOTHING)
    question = models.ForeignKey('Question', default=None, on_delete=models.DO_NOTHING)
    selected_choice = models.ForeignKey('Choice', default=None, on_delete=models.DO_NOTHING)
