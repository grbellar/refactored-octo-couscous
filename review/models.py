from django.db import models
from django.contrib.auth import get_user_model
from base.settings import AUTH_USER_MODEL
from exams.models import Category

# Create your models here.
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
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

class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.SET(get_sentinel_quiz))
    quiz_title_snapshot = models.CharField(blank=True)
    user = models.ForeignKey(
        AUTH_USER_MODEL, 
        on_delete=models.SET(get_sentinel_user),
        default=None
    )
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.quiz and not self.quiz_title_snapshot:
            self.quiz_title_snapshot = self.quiz.title
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"
