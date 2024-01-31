from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from exams.models import Exam, UserExamState


class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


#TODO: Figure out how to add a message to the page. Currently it takes user directly to login screen. 
@login_required
@require_http_methods(["GET"])
def my_exams(request):
        # You can access the current user object from the request! see https://docs.djangoproject.com/en/5.0/topics/auth/default/#authentication-in-web-requests
        user = request.user
        has_paid = user.has_paid
        context = {"user_has_paid": has_paid}

        # This feels wasteful as all I need this for is to get each exam name and id so I can show it to suer and then 
        # send the chosen Exam to the take-exam view.
        all_exams = Exam.objects.all()
        context['exams'] = all_exams


        return render(request, 'exams/my_exams.html', context)
               
     
@login_required
def my_results(request):
    context = {}
    all_results = []
    for exam_state in UserExamState.objects.filter(user_id=request.user.id):

        if exam_state.completed:
            if exam_state.exam == None:
                exam_name = exam_state.exam_name
            else:
                exam_name = exam_state.exam.name
            
            result_dict = {
                "exam_name": exam_name,
                "score": "{:.0f}%".format(exam_state.score),
                "num_correct": exam_state.num_correct, 
                "num_questions": exam_state.num_questions
            }
            
            all_results.append(result_dict)
    
    context["all_results"] = all_results
    
    if not all_results: # If all_results is empty
         context["results"] = False
    else: 
         context["results"] = True

    return render(request, "exams/results.html", context)
     