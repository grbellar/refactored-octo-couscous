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


#TODO: THIS SHOULD FIX THE ISSUE WITH DELETED EXAMS AND QUESTIONS. STORE A COPY OF EXAM AND QUESTION TEXT TO FALL BACK ON.
#       1. Should probably store this data in the database so I'm not grading every time they look at the results page.
#       Better yet, grade an Exam as soon as they finish, that way I have the data for whenever I want to present it to them,
#       weather that is right away or by telling them to view the results page.
def grade(exam, user_answers):
    #TODO: Major todo: If Exam is deleted my current display results logic doesn't work. UserExamState data is protected but don't know what Exam is belonged to.
    # A. Specify a default for when Exam are deleted. That way the Exam field in 
    # question would at least have a name. Would require some complex logic though as Question exam field
    # is expecting type Exam, not a string.
    # B. Could also not allow deletion of exams but this doesn't feel good long term. Though perhaps once in production
    # we won't be deleting any exams?
    # C. Best option. I need to properly handle for deletion of Exams that still allows me to display User results
    # with the name of the deleted exam and perhaps a note explaing that this Exam no longer exists.
    #TODO: Also handle deletion of Questions object which affect UserAnswer data.
    #   A. I think I need to more gracefully present exam results so that deletion of a question doesn't nuke everything
    if exam is not None:
        print(f"Exam: {exam.name}")
    num_questions = exam.questions.count()
    num_correct = 0
    for user_answer in user_answers.all():
        if user_answer.selected_choice.is_correct:
            num_correct+=1
    if num_questions != 0:
        score = num_correct / num_questions * 100
    else:
        #TODO: Properly catch divide by zero error
        score = -999
    print(f"{num_correct}/{exam.questions.count()} | {score}")
    print(f"Exam length: {num_questions} questions.\n")

    return (exam.name, "{:.0f}%".format(score), num_correct, num_questions)
               
     


@login_required
def my_results(request):
    all_results = []
    for exam_state in UserExamState.objects.filter(user_id=request.user.id):
        exam_name, score, num_correct, num_questions = grade(exam_state.exam, exam_state.user_answers)
        result_dict = {
            "exam_name": exam_name,
            "score": score,
            "num_correct": num_correct,
            "num_questions": num_questions
        }
        all_results.append(result_dict)
    
    context = {"all_results": all_results}

    return render(request, "exams/results.html", context)
     
