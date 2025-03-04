from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from exams.models import Exam, UserExamState, ExamType, Category
from review.models import Quiz
from collections import defaultdict
from pathlib import Path
from dotenv import load_dotenv
import os 
import pprint
from django.db.models import Count, F, Q, Case, When, IntegerField
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')


class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


#TODO: Figure out how to add a message to the page. Currently it takes user directly to login screen. 
@login_required
@require_http_methods(["GET"])
def my_exams(request):
        user = request.user
        has_paid = user.has_paid_v2
        context = {"user_has_paid": has_paid}
        exams = Exam.objects.annotate(question_count=Count('questions')).values('name', 'uuid', 'is_active', 'question_count')        
        context['exams'] = exams

        # TODO: add a flag to show user that they have taken exam. button should say view results instead.
        # if exam.userexamstate_set.filter(user=request.user, completed=False):
        #     nontaken_exams.append(exam)

        return render(request, 'exams/my_exams.html', context)


@login_required
@require_http_methods(["GET"])
def choose_quiz_type(request):
    exam_types = ExamType.objects.all().order_by('name')
    #TODO: Pass in Clinical Application, etc... instead of abbreviation
    context = {
        'exam_types': [
            {
                'name': exam_type.name,
                'id': exam_type.id
            }
            for exam_type in exam_types
        ]
    }
    context["user_has_paid"] = request.user.has_paid_v2
    print(context['user_has_paid'])

    return render(request, 'review/choose_quiz_type.html', context)


@login_required
@require_http_methods(["GET"])
def choose_quiz_category(request, quiz_type_name):
    # return all categories and data about quiz type from request
    # Get the ExamType object based on the quiz_type_name
    exam_type = ExamType.objects.get(name=quiz_type_name)
    print(f"Exam type: {exam_type}")
    categories = exam_type.categories.all()
    print(categories)
    
    # Get the current user
    user = request.user
    
    categories_data = []
    for category in categories:
        print("\nCategory info:")
        print(f"ID: {category.id}")
        print(f"Name: {category.name}")
        print(f"Icon: {category.icon}")
        print(f"Exam Type: {category.exam_type}")
        quiz_count = category.quiz_set.count()
        print(f"Quiz count: {quiz_count}")
        completed_quiz_count = Quiz.objects.filter(
            category=category,
            userquizstate__user=user,
            userquizstate__completed=True
        ).count()
        if quiz_count != 0:
            percentage_done = round(completed_quiz_count / quiz_count * 100)
        else:
            percentage_done = 0

        category_data = {
            'id': category.id,
            'name': category.name,
            'icon': category.icon,
            'quiz_count': quiz_count,
            'completed_quiz_count': completed_quiz_count,
            'percentage_done': percentage_done
        }
        categories_data.append(category_data)

    context = {
        'categories': categories_data,
        'exam_type_name': exam_type.name
    }
    
    return render(request, 'review/choose_category.html', context=context)


@login_required
@require_http_methods(["GET"])
def choose_quiz(request, _quiz_type_name, _category_name, category_id):
    
    user = request.user
    has_paid = user.has_paid_v2
    context = {"user_has_paid": has_paid}
    
    # Get the selected category from the request
    selected_category = Category.objects.get(id=category_id)
    print("\nSelected Category Details:")
    print(f"ID: {selected_category.id}")
    print(f"Name: {selected_category.name}")
    print(f"Icon: {selected_category.icon}")
    print(f"Exam Type: {selected_category.exam_type}")
    
    # Debug ALL quizzes in this category before any filtering
    all_quizzes = Quiz.objects.filter(category=selected_category)
    print(f"\nTotal quizzes in category before filtering: {all_quizzes.count()}")
    print("All quiz details:")
    for q in all_quizzes:
        print(f"ID: {q.id}, UUID: {q.uuid}, Title: {q.title}")
        # Check if quiz has questions
        question_count = q.questions.count()
        print(f"  Question count: {question_count}")
        
    # Filter quizzes by quiz_type with the complex query
    quizzes = Quiz.objects.filter(category=selected_category).annotate(
        question_count=Count('questions')
    ).annotate(
        user_state=Case(
            When(userquizstate__user=user, then=F('userquizstate')),
            default=None,
            output_field=IntegerField(),
        )
    ).values(
        'title', 'uuid', 'description', 'question_count',
        'userquizstate__time_started', 'userquizstate__user',
        'userquizstate__completed', 'userquizstate__score', 'category'
    ).annotate(
        in_progress=Case(
            When(
                Q(userquizstate__time_started__isnull=False) & Q(userquizstate__completed=False),
                then=1
            ),
            default=0,
            output_field=IntegerField(),
        ),
        completed=Case(When(userquizstate__completed=True, then=1),
            default=0,
            output_field=IntegerField(),
        )
    ).order_by('-in_progress', '-completed', 'title')

    # Debug after filtering
    print(f"\nTotal quizzes after filtering: {len(quizzes)}")
    print("Filtered quiz details:")
    for q in quizzes:
        print(f"UUID: {q['uuid']}, Title: {q['title']}")
        print(f"  Question count: {q['question_count']}")
        print(f"  User state: {q['userquizstate__user']}")
        print(f"  In progress: {q['in_progress']}")
        print(f"  Completed: {q['completed']}")
    
    # Add is_expired flag, time_remaining, not_started, completed, and score to each quiz
    now = timezone.now()
    print(quizzes)  
    for quiz in quizzes:
        # Check if quiz hasn't been started by this user
        quiz['not_started'] = quiz['userquizstate__user'] is None
        
        time_started = quiz['userquizstate__time_started']
        if time_started is not None:
            time_elapsed = now - time_started
            is_expired = time_elapsed >= timedelta(hours=8)
            quiz['is_expired'] = is_expired
            if not is_expired:
                time_remaining = timedelta(hours=8) - time_elapsed
                # Convert timedelta to hours and minutes
                total_minutes = time_remaining.total_seconds() / 60
                hours = int(total_minutes // 60)
                minutes = int(total_minutes % 60)
                quiz['hours_remaining'] = hours
                quiz['minutes_remaining'] = minutes
        else:
            quiz['is_expired'] = False
            quiz['hours_remaining'] = None
            quiz['minutes_remaining'] = None
        
        # Check if the quiz is completed and add score
        quiz['completed'] = quiz['userquizstate__completed']
        if quiz['completed']:
            quiz['score'] = quiz['userquizstate__score']
        else:
            quiz['score'] = None
    
    # Implement pagination
    paginator = Paginator(quizzes, 10)  # Show 10 quizzes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(f"Page obj: {page_obj}")
    for obj in page_obj:
        print(obj)
    print(selected_category)

    context['page_obj'] = page_obj
    context['selected_category'] = selected_category
    context['quiz_type'] = _quiz_type_name
    context['category_name'] = _category_name

    return render(request, 'review/choose_quiz.html', context)

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
    exam = exam_result.exam

    #TODO: This should be refactored into my grade method so the data can be saved in the database.
    #   I don't think I want to be running this computation every time a user looks at their results.
    #TODO: Store category_scores_list as a JSONField in my UserExamState model.

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
    
    total_answers = 0
    for category in category_scores_list:
        total_answers = total_answers + category["total"]

    total_questions = exam.questions.all().count()

    unanswered = total_questions - total_answers

    context = {
        "exam_result": exam_result,
        "category_scores": category_scores_list,
        "user_full_name": f"{request.user.first_name} {request.user.last_name}",
        "unanswered": unanswered
    }
    
    return render(request, "exams/results_single.html", context)


def get_access_buy(request):
    PRICE_ID_FULL_ACCESS = os.getenv('PRICE_ID_FULL_ACCESS')
    context = {
        "fullaccess": PRICE_ID_FULL_ACCESS,
    }
    return render(request, "pages/get_access_buy.html", context)
