from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .models import *


def save_user_progress(question, choice):
    # IDK might not be worth a seperate function.
    pass


@require_http_methods(['GET', 'POST'])  
def take_exam_view(request, uuid):
    
    exam = Exam.objects.get(uuid=uuid)
    # Get UserExamState instance or create one if it doesn't exist. created is a boolean indicating whether the 
    # UserExamState object was just created.
    user_exam_state, created = UserExamState.objects.get_or_create(
        user=request.user,
        exam=exam,
    )
    
    if user_exam_state.completed:
        return redirect("exam-complete", permanent=True)
        

    else:
        exam_questions = list(exam.question.all()) # wrapping this in a list to make this easier to work with
        print(exam_questions)
        current_question_index = user_exam_state.current_question_index
        print(f"{request.user.username}: {current_question_index}")
        current_question = exam_questions[current_question_index]

        context = {"exam": exam,
                "question": current_question,
                "user_exam_state": user_exam_state,
                "DEBUG": True}
        
        if request.method == 'POST':
            user_choice = request.POST.get('user_choice')
            selected_choice_obj = Choice.objects.get(id=user_choice)
            UserAnswer.objects.create(
                user_exam_state=user_exam_state,
                question=current_question,
                selected_choice=selected_choice_obj
            )
            
            current_question_index +=1

            if current_question_index >= len(exam_questions):
                user_exam_state.completed = True
            
            user_exam_state.current_question_index = current_question_index
            user_exam_state.save()
            
            if user_exam_state.completed:
                return redirect("exam-complete", permanent=True)
            else:
                next_question = exam_questions[user_exam_state.current_question_index]
                context['question'] = next_question

        return render(request, "exams/take_exam.html", context)


def exam_complete(request):
     # TODO: This doesn't feel quite right. Feel like I should pass Exam specific context and idk
     # if this being a permanent redirect is good.
     return render(request, "exams/exam_complete.html")