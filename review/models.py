from django.db import models
from django.contrib.auth import get_user_model
from base.settings import AUTH_USER_MODEL

# Create your models here.
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # need something to store stats about user responses. e.g. how many users got question right/wrong
    stats = models.JSONField(default=dict, null=True) # not sure if this is the best way to store stats. ai suggested it.

    def __str__(self):
        return self.title
        
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_DEFAULT, default=None, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text
    
    # apparently 'sentinel' user is a common pattern to handle data integrity when a user is deleted.
def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]

class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(
        AUTH_USER_MODEL, 
        on_delete=models.SET(get_sentinel_user),
        default=None
    )
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"
