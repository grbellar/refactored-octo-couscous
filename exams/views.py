from django.shortcuts import render
from django.views.generic import TemplateView
from .models import *

            
def question_view(request, pk):
    current_question = Question.objects.get(id=pk)
    context = {"question": current_question}
    
    if request.method == 'GET':
        return render(request, 'exams/question.html', context)
    
    if request.method == 'POST':
        user_choice = request.POST.get('user_choice')
        is_user_choice_correct = Choice.objects.get(id=user_choice).is_correct
        print(user_choice)
        print(is_user_choice_correct)
        pk +=1
        next_question = Question.objects.get(id=pk)
        context['question'] = next_question
        context['is_correct'] = is_user_choice_correct
        return render(request, 'exams/question.html', context)


class TakeExamView(TemplateView):
    template_name = 'exams/take_exam.html'

# Need a way better way to store which choice a user made. Right now there might be 500 choices and a 
    # choice would be Choice23 which doesn't tell me which question it belongs to.