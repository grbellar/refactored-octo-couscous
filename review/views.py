from django.shortcuts import render, redirect
import json
from .models import Quiz, UserQuizState, Answer, UserQuizAnswer
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import requires_csrf_token
import pprint


with open('review/test-review-data.json', 'r') as file:
    quizzes = json.load(file)


def get_user_answer(user, quiz_uuid, question):
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    user_quiz_state = UserQuizState.objects.get(user=user, quiz=quiz)
    user_answer = UserQuizAnswer.objects.get(user_quiz_state=user_quiz_state, question=question)
    pprint.pprint(user_answer.selected_answer.id)
    return user_answer


def get_quiz_question(user, quiz_uuid):
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    quiz_state= UserQuizState.objects.get_or_create(user=user, quiz=quiz)[0]
    quiz_question = quiz.questions.all()[quiz_state.current_question_index]
    question_data = {
        'question_id': quiz_question.id,
        'question_number': quiz_state.current_question_index + 1,
        'question_text': quiz_question.text,
        'answers': list(quiz_question.answer_set.values('id', 'text', 'choice_count')),
        'explanation': quiz_question.explanation.text,
        'total_questions': quiz.questions.count(),
        'is_first_question': quiz_state.current_question_index == 0,
        'is_last_question': quiz_state.current_question_index == quiz.questions.count() - 1,
    }
    # If user answer exists, add it to the question data
    try:
        user_answer = get_user_answer(user, quiz_uuid, quiz_question)
        question_data['user_answer_id'] = user_answer.selected_answer.id
        question_data['is_correct'] = user_answer.is_correct
    except (AttributeError, UserQuizAnswer.DoesNotExist):
        # Handle case where user_answer or its attributes don't exist
        print("User answer does not exist")
    pprint.pprint(question_data)
    return question_data




@login_required
@require_http_methods(['GET']) 
def take_quiz(request, quiz_uuid):
    context = get_quiz_question(request.user, quiz_uuid)
    context['quiz_title'] = Quiz.objects.get(uuid=quiz_uuid).title
    context['quiz_uuid'] = quiz_uuid
    # Initial page load
    return render(request, "review/take_quiz.html", context=context)


@login_required
@require_http_methods(['POST']) 
def save_answer(request, quiz_uuid):
    #TODO: Save to db
    # Get answer id
    # Send back is correct
    # Needs to send back is_last_question so I can disable next button
    question_data = get_quiz_question(request.user, quiz_uuid)
    return JsonResponse(question_data)


@login_required
@require_http_methods(['POST']) 
def update_question_index(request, quiz_uuid):
    # Update index in db and return new question data
    direction = int(request.POST.get('direction'))
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    user_quiz_state = UserQuizState.objects.get(user=request.user, quiz=quiz)

    if user_quiz_state.current_question_index == 0 and direction == -1:
        # Prevent negative index
        return JsonResponse({
            'status': "Already on first question!"
        })
    elif user_quiz_state.current_question_index == quiz.questions.count() - 1 and direction == 1:
        # Prevent index out of range
        return JsonResponse({
            'status': "Already on last question!"
        })
    else:
        user_quiz_state.current_question_index += direction
        user_quiz_state.save()
        question_data = get_quiz_question(request.user, quiz_uuid)
        return JsonResponse(question_data)



@login_required
@require_http_methods(['POST'])
@requires_csrf_token
def check_answer(request, quiz_uuid):
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    user_quiz_state = UserQuizState.objects.get(user=request.user, quiz=quiz)
    current_question = get_quiz_question(quiz_uuid, user_quiz_state.current_question_index)
    
    print(f"Check answer button clicked: current_question_index: {user_quiz_state.current_question_index}") # At this point should still match inital page load
        
    # Save new answer
    user_answer_id = request.POST.get('user_answer')
    selected_answer = Answer.objects.get(id=user_answer_id)
    # UserQuizAnswer.objects.create(
    #     user_quiz_state=user_quiz_state,
    #     question=current_question,
    #     selected_answer=selected_answer,
    #     is_correct=selected_answer.is_correct
    # )
    
    # Check if this was the last question.
    # If so:
    # 1. Save the user quiz state as completed
    # 2. Tell front end not to display next on the last question
    # is_last_question = user_quiz_state.current_question_index == quiz.questions.count() - 1
    # if is_last_question:
    #     user_quiz_state.completed = True
    #     user_quiz_state.save()
    #     return JsonResponse({
    #         'is_last_question': is_last_question
    #     })
    