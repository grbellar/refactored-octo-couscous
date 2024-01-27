from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from exams.models import Exam, UserAnswer, UserExamState


class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


#TODO: Figure out how to add a message to the page. Currently it takes user directly to login screen. 
@login_required
@require_http_methods(["GET"])
def my_exams(request):
        # it appears you can access the current user object from the request. see https://docs.djangoproject.com/en/5.0/topics/auth/default/#authentication-in-web-requests
        user = request.user
        has_paid = user.has_paid
        context = {"user_has_paid": has_paid}

        # This feels wasteful as all I need this for is to get each exam name and id so I can show it to suer and then 
        # send the chosen Exam to the take-exam view.
        all_exams = Exam.objects.all()
        context['exams'] = all_exams


        return render(request, 'exams/my_exams.html', context)


def grade(exam, user_answers):
    print(f"Exam: {exam.name}")
    num_questions = exam.questions.count()
    num_correct = 0
    for user_answer in user_answers.all():
        if user_answer.selected_choice.is_correct:
            num_correct+=1
    if num_questions != 0:
        score = num_correct / num_questions
    else:
        score = -999
    print(f"{num_correct}/{exam.questions.count()} | {score}")
    print(f"Exam length: {num_questions} questions.\n")
               
     


@login_required
def my_results(request):
    for exam_state in UserExamState.objects.filter(user=request.user):
        grade(exam_state.exam, exam_state.user_answers)

    return render(request, "exams/results.html")
     
