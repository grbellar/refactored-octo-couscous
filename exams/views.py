from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View
from .models import *

# Create your views here.
class SingleQuestionView(DetailView):
    model = Question
    template_name = 'exams/question.html' 

    def post(self, request, *args, **kwargs):
        print(request.POST.get('1'))
        return HttpResponseRedirect('')


class HandleQuestionSubmissions(View):
    template_name = 'exams/form_success.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

    def post(self, request, *args, **kwargs):
        print(request.POST.get())
        return HttpResponseRedirect('/exams/success/')



# TODO: Can I use a DetailView and FormView together? Where do I send the form data? Work on how to
    # submit form answers and get next question. 