import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from exams.models import Exam

class CustomUser(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # Using this for url parameters    
    has_paid = models.BooleanField(default=False, null=False)
    exam_tokens = models.IntegerField(default=0, null=False, blank=False) # Maybe this could be its own model?
    exam = models.ManyToManyField(Exam)
    school = models.CharField(max_length=300, null=True, blank=True)
    
    
    #TODO: Figure out why my customer fields aren't showing up in the Django User admin panel.
    def __str__(self):
        return self.email