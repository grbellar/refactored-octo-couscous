from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from .models import Quiz, UserQuizState, Answer, UserQuizAnswer, Question
from django.db import transaction


def grade_quiz(quiz_state):
    num_correct = 0 
    user_answers = quiz_state.user_answers.all()
    score = 0
    for answer in user_answers:
        if answer.is_correct:
            num_correct +=1
    if user_answers.count() > 0:
        score = num_correct / user_answers.count()
    quiz_state.score = score * 100
    quiz_state.save()


@login_required
@require_http_methods(['POST']) 
def set_quiz_complete(request, quiz_uuid):
    is_complete = int(request.POST.get('complete'))
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    user_quiz_state = UserQuizState.objects.get(user=request.user, quiz=quiz)
    if is_complete:
        user_quiz_state.completed = True
        user_quiz_state.time_completed = timezone.now()
        user_quiz_state.save()
        grade_quiz(user_quiz_state)
        return JsonResponse({'status': 'success'}, status=200)
    return JsonResponse({'status': 'got bad is_complete variable'}, status=400)

def get_user_answer(user, quiz_uuid, question):
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    user_quiz_state = UserQuizState.objects.get(user=user, quiz=quiz)
    user_answer = UserQuizAnswer.objects.get(user_quiz_state=user_quiz_state, question=question)
    return user_answer


def get_quiz_question(user, quiz_uuid):
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    quiz_state= UserQuizState.objects.get_or_create(user=user, quiz=quiz)[0]
    quiz_question = quiz.questions.all()[quiz_state.current_question_index]
    question_data = {
        'question_id': quiz_question.id,
        'question_number': quiz_state.current_question_index + 1,
        'category': quiz_question.category.name,
        'category_id': quiz_question.category.id,
        'question_text': quiz_question.text,
        'answers': list(quiz_question.answer_set.values('id', 'text', 'choice_count')),
        'explanation': quiz_question.explanation.text,
        'sources': quiz_question.explanation.sources,
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
        'quiz_type': quiz.quiz_type,
        'time_started': start_time.isoformat(),
        'time_ends': end_time.isoformat(),
    })
    return render(request, "review/take_quiz.html", context=context)


@login_required
@require_http_methods(['POST']) 
def save_answer(request, quiz_uuid):
    

    chosen_answer_id = request.POST.get('user_answer')
    chosen_answer = Answer.objects.get(id=chosen_answer_id)
    chosen_answer.choice_count += 1
    chosen_answer.save()

    quiz = Quiz.objects.get(uuid=quiz_uuid)
    quiz_state= UserQuizState.objects.get(user=request.user, quiz=quiz)
    quiz_question = quiz.questions.all()[quiz_state.current_question_index]

    # TODO: Should prob add a check for completed quiz state but oh well.

    UserQuizAnswer.objects.create(
        user_quiz_state=quiz_state,
        question=quiz_question,
        selected_answer=chosen_answer,
        is_correct=chosen_answer.is_correct
    )

    # Needs to be last call so that user answer data is available to show and pass back to front end
    question_data = get_quiz_question(request.user, quiz_uuid)
    if question_data['is_last_question']:
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


@login_required
@require_http_methods(['POST']) 
def save_feedback(request, quiz_uuid):
    reason = request.POST.get('reason')
    reason_explained = request.POST.get('reason-explained')
    print(reason)
    print(reason_explained)
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    quiz_state= UserQuizState.objects.get(user=request.user, quiz=quiz)
    quiz_question = quiz.questions.all()[quiz_state.current_question_index]
    
    # Add flag to the question
    quiz_question.add_flag(request.user, reason, reason_explained)

    return JsonResponse({'status': 'feedback saved'}, status=200)