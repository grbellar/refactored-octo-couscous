from django.db import models

# When defining a relationship involiving my custom user model this is how I should refer to it. settings.AUTH_USER_MODEL
# from django docs https://docs.djangoproject.com/en/dev/topics/auth/customizing/#substituting-a-custom-user-model
# class Article(models.Model):
#     author = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#     )