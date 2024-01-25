from django.contrib.auth.models import AbstractUser
from django.db import models
from exams.models import Exam

class CustomUser(AbstractUser):
    has_paid = models.BooleanField(default=False, null=False)
    exam = models.ManyToManyField(Exam)
    #TODO: Figure out why my customer fields aren't showing up in the Django User admin panel.

    #TODO: Add a UUID field so that I can pass that to stripe and use that to identify users. Better than using sequential integers

    def check_with_stripe():
        # Not sure if I'll need this. Stubbing for now. Return True or False if paid.
        pass


# Note sure what this is for as the display is defined in the CustomUserAdmin class (admin.py).
    def __str__(self):
        return self.email