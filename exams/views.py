from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from exams.models import Exam
from .models import *


@require_http_methods(['GET', 'POST'])       
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


def take_exam_view(request, pk):
    user = request.user
    # Should maybe see if we can make this happen
    # when a user creates their account. Users should automatically be given a copy of all exams. ACTUALLY it should be when a user pays.
    # Creating them when a user registers my be a waste if they dont' end up paying. Of course if the only way to register is to pay then this
    # point is moot.
    user.add(Exam.objects.get(id=pk))
    user.save()

    user_instance_of_exam = user.exam
    context = {"exam": user_instance_of_exam}
    return render(request, "exams/take_exam.html", context)


# Need a way better way to store which choice a user made. Right now there might be 500 choices and a 
    # choice would be Choice23 which doesn't tell me which question it belongs to.