from django.shortcuts import render, redirect
import json
from .models import Quiz, UserQuizState, Answer, UserQuizAnswer
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import requires_csrf_token


with open('review/test-review-data.json', 'r') as file:
    quizzes = json.load(file)

def get_quiz_question(quiz_uuid, question_index):
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    print(quiz.question_set.all())
    quiz_question = quiz.question_set.all()[question_index]
    return quiz_question


@login_required
@require_http_methods(['GET']) 
def take_quiz(request, quiz_uuid): # TODO: this should become get_quiz prob. All its doing is setting the starting state of the quiz from a GET request.
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    user_quiz_state = UserQuizState.objects.get_or_create(user=request.user, quiz=quiz)[0]
    current_question = get_quiz_question(quiz_uuid, user_quiz_state.current_question_index)
    print(current_question)
    # Initial page load
    return render(request, "review/take_quiz.html", {'quiz': quiz, 'current_question': current_question})


@login_required
@require_http_methods(['POST'])
@requires_csrf_token
def check_answer(request, quiz_uuid):
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    user_quiz_state = UserQuizState.objects.get(user=request.user, quiz=quiz)
    
    button_clicked = request.POST.get('button')
    current_question = get_quiz_question(quiz_uuid, user_quiz_state.current_question_index)

    # Handle navigation in review mode
    if user_quiz_state.completed:
        if button_clicked == 'back-btn' and user_quiz_state.current_question_index > 0:
            user_quiz_state.current_question_index -= 1
        elif button_clicked == 'check-answer-btn' and user_quiz_state.current_question_index < quiz.question_set.count() - 1:
            user_quiz_state.current_question_index += 1
        user_quiz_state.save()
        # TODO: Also update time stamp
        
        current_question = get_quiz_question(quiz_uuid, user_quiz_state.current_question_index)
        # Get the user's previous answer for this question
        saved_answer = UserQuizAnswer.objects.get(
            user_quiz_state=user_quiz_state,
            question=current_question
        )
        
        return JsonResponse({
            'is_correct': saved_answer.is_correct,
            'explanation': current_question.explanation,
            'is_complete': True,
            'current_question_index': user_quiz_state.current_question_index,
            'total_questions': quiz.question_set.count()
        })

    # TODO: current_question_index is not saving to db correcty
    if button_clicked == 'check-answer-btn':
        user_answer_id = request.POST.get('user_answer')
        selected_answer = Answer.objects.get(id=user_answer_id)
        UserQuizAnswer.objects.create(
            user_quiz_state=user_quiz_state,
            question=current_question,
            selected_answer=selected_answer,
            is_correct=selected_answer.is_correct
        )
        
        return JsonResponse({
            'is_correct': selected_answer.is_correct,
            'explanation': current_question.explanation.text if hasattr(current_question.explanation, 'text') else current_question.explanation
        })

    if button_clicked == 'next-btn':    
        is_last_question = user_quiz_state.current_question_index == quiz.question_set.count() - 1
        
        if not is_last_question:
            user_quiz_state.current_question_index += 1
            user_quiz_state.save()
            next_question = get_quiz_question(quiz_uuid, user_quiz_state.current_question_index)
            
            return JsonResponse({
                'next_question': {
                    'text': next_question.text,
                    'answers': list(next_question.answer_set.values('id', 'text'))
                },
                'is_complete': user_quiz_state.completed,
                'current_question_index': user_quiz_state.current_question_index,
                'total_questions': quiz.question_set.count()
            })
        else:
            user_quiz_state.completed = True
            user_quiz_state.save()
            return JsonResponse({
                'is_complete': True,
                'message': 'Quiz completed'
            })
    elif button_clicked == 'back-btn':
        if user_quiz_state.current_question_index > 0:
            user_quiz_state.current_question_index -= 1
            user_quiz_state.save()
            
        prev_question = get_quiz_question(quiz_uuid, user_quiz_state.current_question_index)
        # Get the user's previous answer for this question
        previous_answer = UserQuizAnswer.objects.get(
            user_quiz_state=user_quiz_state,
            question=prev_question
        )
        
        return JsonResponse({
            'next_question': {
                'text': prev_question.text,
                'answers': list(prev_question.answer_set.values('id', 'text'))
            },
            'previous_answer': {
                'selected_answer_id': previous_answer.selected_answer.id,
                'is_correct': previous_answer.is_correct,
                'explanation': prev_question.explanation
            },
            'is_complete': user_quiz_state.completed,
            'current_question_index': user_quiz_state.current_question_index,
            'total_questions': quiz.question_set.count()
        })