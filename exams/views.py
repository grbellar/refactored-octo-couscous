from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .models import *


# @require_http_methods(['GET', 'POST'])       
# def question_view(request, pk):
#     current_question = Question.objects.get(id=pk)
#     context = {"question": current_question}
    
#     if request.method == 'GET':
#         return render(request, 'exams/question.html', context)
    
#     if request.method == 'POST':
#         user_choice = request.POST.get('user_choice')
#         is_user_choice_correct = Choice.objects.get(id=user_choice).is_correct
#         print(user_choice)
#         print(is_user_choice_correct)
#         pk +=1
#         next_question = Question.objects.get(id=pk)
#         context['question'] = next_question
#         context['is_correct'] = is_user_choice_correct
#         return render(request, 'exams/question.html', context)


def take_exam_view(request, pk):
    # Need to figure out how to make sure I am storing user specific exam data as they begin taking this exam. See previous commit for 
    # comments on one approach with giving each user an Exam.
    #TODO: See take_exam.html
    exam = Exam.objects.get(id=pk)
    exam_questions = exam.question.all()

    first_question = exam_questions.first()
    current_question = 1
    context = {"exam": exam,
               "question": first_question}    # TODO: Surely I can reverse this query and get the exam name from question without the need to pass exam.

    
    if request.method == 'GET':
        return render(request, "exams/take_exam.html", context)
    if request.method == 'POST':
        user_choice = request.POST.get('user_choice')
        is_user_choice_correct = Choice.objects.get(id=user_choice).is_correct
        current_question +=1
        next_question = exam_questions.get(id=current_question)
        context['question'] = next_question
        context['is_correct'] = is_user_choice_correct
        return render(request, 'exams/question.html', context)


# Need a way better way to store which choice a user made. Right now there might be 500 choices and a 
    # choice would be Choice23 which doesn't tell me which question it belongs to.