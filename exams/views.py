from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import *
import json


def save_user_progress(question, choice):
    # IDK might not be worth a seperate function.
    pass

def question_to_dict(question):
    dict = {}
    dict["text"] = question.text
    dict["choices"] = []
    for choice in question.choices.all():
        dict["choices"].append({"text": choice.text, "id": choice.id,})
    return dict

def grade(user_exam_state):
    num_questions = user_exam_state.exam.questions.count()
    num_correct = 0
    for user_answer in user_exam_state.user_answers.all():
        if user_answer.selected_choice.is_correct:
            num_correct+=1
    if num_questions != 0:
        score = num_correct / num_questions * 100
    else:
        #TODO: Properly catch divide by zero error. Don't think this matters. A real Exam that has just been completed will never have 0 questions.
        score = -999
    
    print(f"{num_correct}/{user_exam_state.exam.questions.count()} | {score}")
    print(f"Exam length: {num_questions} questions.\n")
    
    user_exam_state.score = score
    user_exam_state.num_correct = num_correct
    user_exam_state.num_questions = num_questions
    user_exam_state.graded = True
    
    user_exam_state.save()

#TODO: The javascript works quite well at counting down and redirecting after a certain amount of time. The issue is I am 
    # making a new request each time they hit next question. I need to pass all questions to template and have javascript render them I 
    # think. Also then need template to call grade method. Would require completely reworking take_exam_view.

@login_required
@require_http_methods(['GET', 'POST']) 
def take_exam_view(request, uuid):
    
    exam = Exam.objects.get(uuid=uuid)
    # Get UserExamState instance or create one if it doesn't exist.
    user_exam_state, state_created = UserExamState.objects.get_or_create(
        user=request.user,
        exam=exam,
    )

    if state_created:
        user_exam_state.exam_name = exam.name # Store Exam name for retrival in case of deletion. TODO: If Exam name changes this does not update
        user_exam_state.save()
    
    if user_exam_state.completed:
        # context = {
        #     "exam_uuid": user_exam_state.exam.uuid
        # }
        # print(user_exam_state.exam.uuid)
        return redirect("exam-complete", permanent=True)
        
    else:
        exam_questions = list(exam.questions.all()) # wrapping this in a list to make this easier to work with
        current_question_index = user_exam_state.current_question_index
        current_question = exam_questions[current_question_index]
        context = {
                "exam": exam,
                "question": current_question,
                "user_exam_state": user_exam_state, # only passing this for debug purposes
                "DEBUG": False,
                }
        if request.method == 'GET':
            return render(request, "exams/take_exam.html", context)
        
        if request.method == 'POST':
            user_choice = request.POST.get('user_choice')
            print(user_choice)
            #TODO: Require user to make a choice. Currently you can just hit next!
            selected_choice_obj = Choice.objects.get(id=user_choice)
            UserAnswer.objects.create(
                user_exam_state=user_exam_state,
                question=current_question,
                question_text=current_question.text,
                selected_choice=selected_choice_obj,
                choice_text=selected_choice_obj.text
            )
            
            current_question_index +=1

            if current_question_index >= len(exam_questions):
                user_exam_state.completed = True
            
            user_exam_state.current_question_index = current_question_index
            user_exam_state.save()
            
            if user_exam_state.completed:
                grade(user_exam_state)
                #TODO: Prob display the single result or just redirect to page and thell them to view results.
                return redirect("exam-complete", permanent=True)
            else:
                next_question = exam_questions[user_exam_state.current_question_index]
                data = question_to_dict(next_question)
                return JsonResponse(data)


@login_required
@require_http_methods(["GET"])
def exam_complete(request):
     # TODO: This doesn't feel quite right. Feel like I should pass Exam specific context and idk
     # if this being a permanent redirect is good.
     return render(request, "exams/exam_complete.html")


@require_http_methods(['GET', 'POST'])
def test_ajax_request(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    test_qs = ["Item1", "Item2", "Item3"]
    cur_item = 0
    if is_ajax:
        if request.method == 'GET':
            return JsonResponse({'item': test_qs[0]})
        if request.method == 'POST':
            cur_item +=1
            data = json.load(request)
            message = data.get('payload')
            print(message)
            return JsonResponse({'item': test_qs[cur_item]})
        return JsonResponse({'status': 'Invalid Request'}, status=400)
    
    else:
        return HttpResponseBadRequest('Invalid request')