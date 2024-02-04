from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from exams.models import Exam, UserExamState
from collections import defaultdict
from allauth.account.views import SignupView


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
@require_http_methods(["GET"])
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
                "id": exam_state.id,
                "exam_name": exam_name,
                "score": exam_state.score,
                "num_correct": exam_state.num_correct, 
                "num_questions": exam_state.num_questions
            }
            print(result_dict)
            all_results.append(result_dict)
    
    context["all_results"] = all_results
    
    if not all_results: # If all_results is empty
         context["results"] = False
    else: 
         context["results"] = True

    return render(request, "exams/results.html", context)

@login_required
@require_http_methods(["GET"])
def single_result(request, id):

    exam_result = UserExamState.objects.get(id=id)

    #TODO: This should be refactored into my grade method so the data can be saved in the database.
    #   I don't think I want to be running this computation every time a user looks at their results.

    # Initialize a list to store the data for each category.
    category_scores_list = []

    # Create a dictionary to store the count of correct questions and total questions for each category.
    category_data = defaultdict(lambda: {'correct': 0, 'total': 0})

    # Loop through UserAnswer instances associated with the given UserExamState.
    for user_answer in exam_result.user_answers.all():
        question = user_answer.question
        category_name = question.category.name

        category_data[category_name]['total'] += 1

        if user_answer.selected_choice.is_correct:
            # Check if the selected choice is correct and increment the count of correct questions.
            category_data[category_name]['correct'] += 1

    # Convert the defaultdict to a list of dictionaries with the desired keys.
    for category_name, data in category_data.items():
        category_scores_list.append({'name': category_name, 'correct': data['correct'], 'total': data['total']})

    #TODO: Store this data in a JSONField in my UserExamState model.

    context = {
        "exam_result": exam_result,
        "category_scores": category_scores_list,
        "user_full_name": f"{request.user.first_name} {request.user.last_name}"
    }
    
    return render(request, "exams/results_single.html", context)


def get_access_buy(request):
    return render(request, "pages/get_access_buy.html")


def get_access_overview(request):
    return render(request, "pages/get_access_overview.html")
