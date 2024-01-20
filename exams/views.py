from django.shortcuts import render
from .models import *


def question_view(request, pk):
    current_question = Question.objects.get(id=pk)
    context = {"question": current_question}
    if request.method == 'GET':
        return render(request, 'exams/question.html', context)
    if request.method == 'POST':
        print(request.POST.get('user_answer'))



# TODO: Can I use a DetailView and FormView together? Where do I send the form data? Work on how to
    # submit form answers and get next question.
