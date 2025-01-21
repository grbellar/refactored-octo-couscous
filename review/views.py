from django.shortcuts import render, redirect
import json
from .models import Quiz, UserQuizState, Answer, UserQuizAnswer, Question
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import requires_csrf_token
from django.utils import timezone
import pprint


def grade_quiz(quiz_state):
    num_correct = 0
    for answer in quiz_state.user_answers.all():
        if answer.is_correct:
            num_correct +=1
    score = num_correct / quiz_state.answers.count()

    quiz_state.score = score * 100
    quiz_state.save()
    # save to db


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
        'category': quiz_question.category.name,
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
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    quiz_state = UserQuizState.objects.get(user=request.user, quiz=quiz)
    
    # Calculate end time in UTC
    start_time = quiz_state.time_started
    end_time = start_time + timezone.timedelta(hours=8)
    
    context.update({
        'quiz_title': quiz.title,
        'quiz_uuid': quiz_uuid,
        'time_started': start_time.isoformat(),
        'time_ends': end_time.isoformat(),
    })
    return render(request, "review/take_quiz.html", context=context)


@login_required
@require_http_methods(['POST']) 
def save_answer(request, quiz_uuid):
    

    chosen_answer_id = request.POST.get('user_answer')
    chosen_answer = Answer.objects.get(id=chosen_answer_id)
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    quiz_state= UserQuizState.objects.get(user=request.user, quiz=quiz)
    quiz_question = quiz.questions.all()[quiz_state.current_question_index]

    # TODO: Should prob add a check for completed quiz state but oh well.

    print(request.POST)
    print(request.POST.get('user_answer'))
    UserQuizAnswer.objects.create(
        user_quiz_state=quiz_state,
        question=quiz_question,
        selected_answer=chosen_answer,
        is_correct=chosen_answer.is_correct
    )

    # Needs to be last call so that user answer data is available to show and pass back to front end
    question_data = get_quiz_question(request.user, quiz_uuid)
    if question_data['is_last_question']:
        # TODO: Calculate score
        grade_quiz(quiz_state)
        quiz_state.completed = True
        quiz_state.time_completed = timezone.now()
        quiz_state.save()

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
