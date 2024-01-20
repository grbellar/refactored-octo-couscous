from django.db import models

# https://chat.openai.com/share/788b0c0f-c032-4fd4-a65a-d9c156a36419 

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

# TODO: Run migrations and insert some data into these tables so I can test relationships and displaying 
    # them. 2. Build correct/incorrect functionality so I can test that. Need to figure out what relationships are needed
    # and whether they are working correctly together.