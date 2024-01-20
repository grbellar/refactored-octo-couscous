from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from exams.models import Exam


class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


#TODO: Figure out how to add a message to the page. Currently it takes user directly to login screen. 
@login_required
@require_http_methods(["GET"])
def my_exams_view(request):
        # it appears you can access the current user object from the request. see https://docs.djangoproject.com/en/5.0/topics/auth/default/#authentication-in-web-requests
        user = request.user
        has_paid = user.has_paid
        context = {"user_has_paid": has_paid}

        # This feels wasteful as all I need this for is to get each exam name and id so I can show it to suer and then 
        # send the chosen Exam to the take-exam view.
        all_exams = Exam.objects.all()
        context['exams'] = all_exams


        return render(request, 'exams/my_exams.html', context)

