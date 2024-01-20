from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    has_paid = models.BooleanField(default=False, null=False)


# Note sure what this is for as the display is defined in the CustomUserAdmin class (admin.py).
    def __str__(self):
        return self.email