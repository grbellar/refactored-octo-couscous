from django.contrib.auth.models import AbstractUser
from django.db import models
from exams.models import Exam

class CustomUser(AbstractUser):
    # TODO: Redefine this class with a UUID as the primary key. Seems much more secure than identifying user by integer (I'm #1)
    has_paid = models.BooleanField(default=False, null=False)
    exam = models.ManyToManyField(Exam)
    #TODO: Figure out why my customer fields aren't showing up in the Django User admin panel.

    def check_with_stripe():
        # Not sure if I'll need this. Stubbing for now. Return True or False if paid.
        pass


# Note sure what this is for as the display is defined in the CustomUserAdmin class (admin.py).
    def __str__(self):
        return self.email