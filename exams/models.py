from django.db import models


class Exam(models.Model):
    name = models.CharField(max_length=300)
    question = models.ManyToManyField('Question')


    def __str__(self):
        return f'{self.name}'



class Question(models.Model):
    question = models.TextField(null=False, blank=False)


    def __str__(self):
        return f'Question {self.id}'


    class Meta:
        ordering = ["id"]


class Choice(models.Model):
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="choices")
    text = models.TextField(null=False, blank=False)
    is_correct = models.BooleanField()

# TODO: 2. Build correct/incorrect functionality so I can test that. Need to figure out what relationships are needed
    # and whether they are working correctly together.