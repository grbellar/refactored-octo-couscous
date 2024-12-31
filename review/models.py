import uuid
from django.db import models
from django.contrib.auth import get_user_model
from base.settings import AUTH_USER_MODEL
from exams.models import Category, ExamType

# Create your models here.
class Quiz(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    quiz_type = models.ForeignKey(ExamType, on_delete=models.SET_NULL, related_name="quizzes", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
        
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_DEFAULT, default=None, null=True)
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    choice_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text
    
class Explanation(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    sources = models.JSONField(default=list, blank=True)
    
def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]

def get_sentinel_quiz(): 
    return Quiz.objects.get_or_create(title="Deleted Quiz", description="This quiz has been deleted")[0]

class UserQuizState(models.Model):
    quiz = models.ForeignKey('Quiz', on_delete=models.SET(get_sentinel_quiz))
    quiz_title_snapshot = models.CharField(max_length=300, blank=True)
    user = models.ForeignKey(
        AUTH_USER_MODEL, 
        on_delete=models.SET(get_sentinel_user),
        default=None
    )
    current_question_index = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    answers = models.ManyToManyField('Question', through='UserQuizAnswer')
    score = models.IntegerField(default=0)
    time_started = models.DateTimeField(auto_now_add=True)
    time_completed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"

    class Meta:
        verbose_name = "User Quiz State"
        # Note: Removing unique_together to allow multiple attempts

    def save(self, *args, **kwargs):
        if self.quiz and not self.quiz_title_snapshot:
            self.quiz_title_snapshot = self.quiz.title
        super().save(*args, **kwargs)

class UserQuizAnswer(models.Model):
    user_quiz_state = models.ForeignKey(UserQuizState, on_delete=models.CASCADE, related_name="user_answers")
    question = models.ForeignKey('Question', on_delete=models.SET_NULL, null=True)
    question_text = models.TextField(null=True, blank=True)  # Snapshot
    selected_answer = models.ForeignKey('Answer', on_delete=models.SET_NULL, null=True)
    answer_text = models.TextField(null=True, blank=True)  # Snapshot
    is_correct = models.BooleanField(default=False)
    time_answered = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.selected_answer:
            self.is_correct = self.selected_answer.is_correct
            self.answer_text = self.selected_answer.text
        if self.question:
            self.question_text = self.question.text
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Question: {self.question.id} for {self.user_quiz_state.user}"
