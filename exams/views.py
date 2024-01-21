from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .models import *


@require_http_methods(['GET', 'POST'])  
def take_exam_view(request, pk):

    exam = Exam.objects.get(id=pk)
    exam_questions = list(exam.question.all()) # wrapping this in a list to make this easier to work with

    # Get UserExamState instance or create one if it doesn't exist. created is a boolean indicating whether the 
    # UserExamState object was just created.
    user_exam_state, created = UserExamState.objects.get_or_create(
        user=request.user,
        exam=exam,
    )
    
    if user_exam_state.completed:
        print('Exam complete')
        pass # TODO: handle exam completion by return somewhere else. The way this is written it will cause an index of range error
            # for current_question_index below if not. May need to refactor this as CHAT may not have the best ideas.

    current_question_index = user_exam_state.current_question_index
    print(current_question_index)
    current_question = exam_questions[current_question_index]

    context = {"exam": exam,
               "question": current_question}
    
    if request.method == 'POST':
        user_choice = request.POST.get('user_choice')
        # TODO: store user choice
        
        current_question_index +=1

        if current_question_index >= len(exam_questions):
            user_exam_state.completed = True
        
        user_exam_state.current_question_index = current_question_index
        user_exam_state.save()
        
        if user_exam_state.completed:
            # redirect to compeltion page. 
            print('Exam complete.')
            pass
        else:
            next_question = exam_questions[user_exam_state.current_question_index]
            context['question'] = next_question

    return render(request, "exams/take_exam.html", context)


# Need a way better way to store which choice a user made. Right now there might be 500 choices and a 
    # choice would be Choice23 which doesn't tell me which question it belongs to.