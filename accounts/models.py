import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from exams.models import Exam

class CustomUser(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # Using this for url parameters    
    has_paid = models.BooleanField(default=False, null=False)
    exam = models.ManyToManyField(Exam)
    #TODO: Figure out why my customer fields aren't showing up in the Django User admin panel.

    #TODO: Add a UUID field so that I can pass that to stripe and use that to identify users. Better than using sequential integers

    def __str__(self):
        return self.email