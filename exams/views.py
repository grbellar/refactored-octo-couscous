from django.shortcuts import render
from .models import *


def question_view(request, pk):
    current_question = Question.objects.get(id=pk)
    context = {"question": current_question}
    
    if request.method == 'GET':
        return render(request, 'exams/question.html', context)
    
    if request.method == 'POST':
        print(request.POST.get('user_answer'))
        pk +=1
        next_question = Question.objects.get(id=pk)
        context['question'] = next_question
        return render(request, 'exams/question.html', context)


# Need a way better way to store which choice a user made. Right now there might be 500 choices and a 
    # choice would be Choice23 which doesn't tell me which question is belongs to.