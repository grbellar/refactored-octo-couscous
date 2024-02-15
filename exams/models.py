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
    questions = models.ManyToManyField('Question', blank=True)
    exam_type = models.ForeignKey("ExamType", on_delete=models.SET_NULL, related_name="exams", null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'


class Category(models.Model):
    name = models.CharField(max_length=300)
    exam_type = models.ForeignKey("ExamType", on_delete=models.SET_NULL, related_name="categories", null=True)

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Question(models.Model):
    text = models.TextField(null=False, blank=False)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, related_name="questions", null=True, blank=True)

    def __str__(self):
        if self.category:
            category_name = self.category.name
        else:
            category_name = "No category assigned"
        return f'Question {self.id} - {category_name}'

    class Meta:
        ordering = ["id"]


class Choice(models.Model):
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="choices")
    text = models.TextField(null=False, blank=False)
    is_correct = models.BooleanField()

    def __str__(self):
        return f'{self.text}'
    
    class Meta:
        verbose_name = "Question Choice"


class UserExamState(models.Model):
    exam = models.ForeignKey('Exam', on_delete=models.SET_NULL, null=True) # "Might not offer exam anymore but still save state"
    exam_name = models.CharField(max_length=300, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    current_question_index = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    answers = models.ManyToManyField('Question', through='UserAnswer')
    graded = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)
    num_correct = models.IntegerField(null=True, blank=True)
    num_questions = models.IntegerField(null=True, blank=True)
    time_started = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.exam}"
    

    class Meta:
        unique_together = ('user', 'exam')  # Ensure one entry per user per exam. #TODO: This could be a problem if we want to allow users to retake exams.
        verbose_name = "User Exam"


class UserAnswer(models.Model):
    user_exam_state = models.ForeignKey(UserExamState, on_delete=models.CASCADE, related_name="user_answers")
    question = models.ForeignKey('Question', default=None, on_delete=models.SET_NULL, null=True)
    question_text = models.TextField(null=True, blank=True)
    selected_choice = models.ForeignKey('Choice', default=None, on_delete=models.SET_NULL, null=True)
    choice_text = models.TextField(null=True, blank=True)

    # Note: Currently not using question text or choice text but it is in place should I decide to display
        # all questions and answers and the question has since been deleted :)

    def __str__(self):
        return f"Question: {self.question.id} for {self.user_exam_state.user}"
