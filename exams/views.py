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

    exam = Exam.objects.get(id=pk)
    exam_questions = list(exam.question.all()) # wrapping this in a list to make this easier to work with

    # Get UserExamProgress instance or create one if it doesn't exist.
    user_progress, created = UserExamProgress.objects.get_or_create(
        user=request.user,
        exam=exam,
    )
    
    if user_progress.completed:
        print('Exam complete')
        pass # handle exam completion by return somewhere else. The way this is written it will cause an index of range error
            # for current_question_index below if not. May need to refactor this as CHAT may not have the best ideas.

    current_question_index = user_progress.current_question_index
    print(current_question_index)
    current_question = exam_questions[current_question_index]

    context = {"exam": exam,
               "question": current_question}
    
    if request.method == 'POST':
        user_choice = request.POST.get('user_choice')
        # store user choice
        
        current_question_index +=1

        if current_question_index >= len(exam_questions):
            user_progress.completed = True
        
        user_progress.current_question_index = current_question_index
        user_progress.save()
        
        if user_progress.completed:
            # redirect to compeltion page. 
            print('Exam complete.')
            pass
        else:
            next_question = exam_questions[user_progress.current_question_index]
            context['question'] = next_question

    return render(request, "exams/take_exam.html", context)

        





    
    # if request.method == 'GET':
    #     return render(request, "exams/take_exam.html", context)
    # if request.method == 'POST':
    #     user_choice = request.POST.get('user_choice')
    #     is_user_choice_correct = Choice.objects.get(id=user_choice).is_correct
    #     current_question +=1
    #     next_question = exam_questions.get(id=current_question)
    #     context['question'] = next_question
    #     context['is_correct'] = is_user_choice_correct
    #     return render(request, 'exams/question.html', context)


# Need a way better way to store which choice a user made. Right now there might be 500 choices and a 
    # choice would be Choice23 which doesn't tell me which question it belongs to.