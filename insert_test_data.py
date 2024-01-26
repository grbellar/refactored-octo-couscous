from exams.models import Exam, Category, Question, Choice


def populate_test_data():
    # Create an Exam
    exam = Exam.objects.create(name="For Testing Only")

    # Create Categories
    math_category = Category.objects.create(name="Mathematics", exam=exam)
    science_category = Category.objects.create(name="Science", exam=exam)

    # Create Questions and Choices for Mathematics Category
    # First two questions
    math_q1 = Question.objects.create(question="What is 10 + 15?", category=math_category)
    Choice.objects.create(question=math_q1, text="25", is_correct=True)
    Choice.objects.create(question=math_q1, text="20", is_correct=False)

    math_q2 = Question.objects.create(question="What is the square root of 81?", category=math_category)
    Choice.objects.create(question=math_q2, text="9", is_correct=True)
    Choice.objects.create(question=math_q2, text="8", is_correct=False)

    # Additional two questions
    math_q3 = Question.objects.create(question="What is 50 divided by 5?", category=math_category)
    Choice.objects.create(question=math_q3, text="10", is_correct=True)
    Choice.objects.create(question=math_q3, text="5", is_correct=False)

    math_q4 = Question.objects.create(question="What is 7 times 6?", category=math_category)
    Choice.objects.create(question=math_q4, text="42", is_correct=True)
    Choice.objects.create(question=math_q4, text="36", is_correct=False)

    # Create Questions and Choices for Science Category
    # First two questions
    science_q1 = Question.objects.create(question="What is the chemical formula for water?", category=science_category)
    Choice.objects.create(question=science_q1, text="H2O", is_correct=True)
    Choice.objects.create(question=science_q1, text="CO2", is_correct=False)

    science_q2 = Question.objects.create(question="What force keeps the planets in orbit around the sun?", category=science_category)
    Choice.objects.create(question=science_q2, text="Gravity", is_correct=True)
    Choice.objects.create(question=science_q2, text="Magnetism", is_correct=False)

    # Additional two questions
    science_q3 = Question.objects.create(question="What is the primary gas in Earth's atmosphere?", category=science_category)
    Choice.objects.create(question=science_q3, text="Nitrogen", is_correct=True)
    Choice.objects.create(question=science_q3, text="Oxygen", is_correct=False)

    science_q4 = Question.objects.create(question="What part of the plant conducts photosynthesis?", category=science_category)
    Choice.objects.create(question=science_q4, text="Leaves", is_correct=True)
    Choice.objects.create(question=science_q4, text="Roots", is_correct=False)

    exam.save()

    print("Test data populated successfully!")

# Call the function to populate the data
populate_test_data()
