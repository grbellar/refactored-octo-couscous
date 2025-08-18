import uuid
from django.db import models
from django.contrib.auth import get_user_model
from base.settings import AUTH_USER_MODEL
from exams.models import Category, ExamType

# Create your models here.
class Quiz(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    quiz_type = models.ForeignKey(ExamType, on_delete=models.SET_NULL, related_name="quizzes", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    questions = models.ManyToManyField('Question', related_name='questions', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
        
class Question(models.Model):
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    flagged = models.BooleanField(default=False)
    flag_reasons = models.JSONField(default=list, blank=True)  # List of flag objects

    def __str__(self):
        return self.text
    
    @property
    def flag_count(self):
        return len(self.flag_reasons) if self.flag_reasons else 0
    
    def add_flag(self, user, reason, reason_explained=None):
        """Add a flag reason to the question"""
        from django.utils import timezone
        
        flag_data = {
            'user_id': user.id,
            'username': user.username,
            'reason': reason,
            'reason_explained': reason_explained,
            'created_at': timezone.now().isoformat()
        }
        
        if not self.flag_reasons:
            self.flag_reasons = []
        
        # Check if user already flagged this question
        for flag in self.flag_reasons:
            if flag.get('user_id') == user.id:
                # Update existing flag
                flag.update(flag_data)
                break
        else:
            # Add new flag
            self.flag_reasons.append(flag_data)
        
        self.flagged = True
        self.save()
    
    def remove_flag(self, user_id):
        """Remove a flag by user ID"""
        if self.flag_reasons:
            self.flag_reasons = [flag for flag in self.flag_reasons if flag.get('user_id') != user_id]
            if not self.flag_reasons:
                self.flagged = False
            self.save()

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
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='explanation')
    text = models.TextField()
    sources = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.text
    
def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]

def get_sentinel_quiz(): 
    return Quiz.objects.get_or_create(title="Deleted Quiz", description="This quiz has been deleted")[0]

class UserQuizState(models.Model):
    quiz = models.ForeignKey('Quiz', on_delete=models.SET_NULL, null=True)
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
        quiz_title = self.quiz.title if self.quiz and self.quiz.title else self.quiz_title_snapshot
        return f"{self.user.username} - {self.quiz.quiz_type} - {quiz_title}"

    class Meta:
        verbose_name = "User Quiz State"
        unique_together = ('user', 'quiz')

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

    class Meta:
        unique_together = ('user_quiz_state', 'question')