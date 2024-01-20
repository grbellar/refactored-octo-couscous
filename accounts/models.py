from django.contrib.auth.models import AbstractUser
from django.db import models
from exams.models import Exam

class CustomUser(AbstractUser):
    has_paid = models.BooleanField(default=False, null=False)
    exam = models.ManyToManyField(Exam)

    def check_with_stripe():
        # Not sure if I'll need this. Stubbing for now. Return True or False if paid.
        pass


# Note sure what this is for as the display is defined in the CustomUserAdmin class (admin.py).
    def __str__(self):
        return self.email