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
    
    # Debug prints
    print("Quiz Question ID:", quiz_question.id)
    print("Quiz Question Fields:", vars(quiz_question))
    print("Quiz Question Dir:", dir(quiz_question))
    print("Explanation:", getattr(quiz_question, 'explanation', 'No explanation found'))
    
    pass


@login_required
@require_http_methods(['GET']) 
def take_quiz(request, quiz_uuid): # TODO: this should become get_quiz prob. All its doing is setting the starting state of the quiz from a GET request.
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    user_quiz_state = UserQuizState.objects.get_or_create(user=request.user, quiz=quiz)[0]
    current_question = get_quiz_question(quiz_uuid, user_quiz_state.current_question_index)
    
    # Initial page load
    return render(request, "review/take_quiz.html", {'quiz': quiz, 'current_question': current_question})


@login_required
@require_http_methods(['POST'])
@requires_csrf_token
def check_answer(request, quiz_uuid):

    # TODO: I need to check for is_complete seperately of whether or not we are on the last question because use can go back and forth once 
    # they have answered all the questions
    quiz = Quiz.objects.get(uuid=quiz_uuid)
    user_quiz_state = UserQuizState.objects.get(user=request.user, quiz=quiz)
    
    if not user_quiz_state.completed:
        # Get the submitted answer ID from the form
        user_answer_id = request.POST.get('user_answer')
        if not user_answer_id:
            return JsonResponse({'error': 'No answer provided'}, status=400)
            
        # Get the selected answer and current question
        selected_answer = Answer.objects.get(id=user_answer_id)
        # TODO: get_quiz_question was supposed to be a way to fetch the next (or previous) question.
        # TODO: Need to check if quiz has ended here.
        current_question = get_quiz_question(quiz_uuid, user_quiz_state.current_question_index) # TODO: Should verify these indexes are accurate
        
        # Save the user's answer
        UserQuizAnswer.objects.create(
            user_quiz_state=user_quiz_state,
            question=current_question,
            selected_answer=selected_answer,
            is_correct=selected_answer.is_correct
        )
        
        # Update quiz state
        if user_quiz_state.current_question_index == len(quiz.question_set.all()) - 1:
            # Reached end of quiz.
            print("Reached end of quiz.")
        else:
            user_quiz_state.current_question_index += 1
            user_quiz_state.save()
            
        # Prepare response data
        # TODO: Need to pass next or previous question as well if not complete
        response_data = {
            'is_correct': selected_answer.is_correct,
            'explanation': current_question.explanation,
            'is_complete': user_quiz_state.current_question_index >= quiz.question_set.count(), # TODO: imp better check here
        }
        
        return JsonResponse(response_data)
    else:
        # Do something else. Maybe a serarate function to handle clicking through questions.
        pass