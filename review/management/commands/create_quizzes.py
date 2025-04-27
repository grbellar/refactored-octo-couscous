import random
import logging
import os
import re
from django.core.management.base import BaseCommand
from review.models import Quiz, Question
from exams.models import Category, ExamType

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
os.makedirs('zlogs', exist_ok=True)

# Create file handler
file_handler = logging.FileHandler('zlogs/create_quizzes.log')
file_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(file_handler)

def get_next_quiz_number(category):
    # Get all existing quizzes for this category
    existing_quizzes = Quiz.objects.filter(category=category)
    
    # Extract numbers from titles
    quiz_numbers = []
    for quiz in existing_quizzes:
        match = re.search(r'(\d+)$', quiz.title)
        if match:
            quiz_numbers.append(int(match.group(1)))
    
    # Return the next number (1 if no existing quizzes)
    return max(quiz_numbers) + 1 if quiz_numbers else 1

class Command(BaseCommand):
    help = 'Create quizzes from unused questions, with a maximum of 10 questions per quiz'

    def handle(self, *args, **options):
        # Fetch all categories
        all_categories = Category.objects.all()
        start_msg = "Starting quiz creation process..."
        self.stdout.write(start_msg)
        logger.info(start_msg)
        
        # First, gather information about what will be created
        preview_data = []
        total_quizzes_to_create = 0
        total_questions_to_use = 0
        
        for category in all_categories:
            # Get all questions for this category that aren't already in any quiz
            unused_questions = Question.objects.filter(
                category=category
            ).exclude(
                questions__isnull=False  # Exclude questions that are already in quizzes
            )
            
            unused_questions = list(unused_questions)
            num_unused = len(unused_questions)
            
            if num_unused == 0:
                continue
            
            # Get existing quizzes that need to be filled
            existing_quizzes = Quiz.objects.filter(category=category)
            quizzes_to_fill = []
            questions_needed_to_fill = 0
            
            for quiz in existing_quizzes:
                current_questions = quiz.questions.count()
                if current_questions < 10:
                    questions_needed = 10 - current_questions
                    quizzes_to_fill.append({
                        'quiz': quiz,
                        'questions_needed': questions_needed
                    })
                    questions_needed_to_fill += questions_needed
            
            # Calculate remaining questions after filling existing quizzes
            remaining_questions = num_unused - questions_needed_to_fill
            if remaining_questions < 0:
                remaining_questions = 0
                
            # Calculate how many new quizzes will be created
            num_new_quizzes = (remaining_questions + 9) // 10  # Round up division
            
            # Get the next quiz number for this category
            next_quiz_number = get_next_quiz_number(category)
            
            preview_data.append({
                'category': f"{category.name} - {category.exam_type.name}",
                'unused_questions': num_unused,
                'quizzes_to_fill': len(quizzes_to_fill),
                'questions_needed_to_fill': questions_needed_to_fill,
                'new_quizzes_to_create': num_new_quizzes,
                'questions_for_new_quizzes': remaining_questions,
                'starting_quiz_number': next_quiz_number
            })
            
            total_quizzes_to_create += num_new_quizzes
            total_questions_to_use += num_unused
        
        # Show preview
        preview_msg = f"\nQuiz Creation Preview:"
        preview_msg += f"\nTotal New Quizzes to Create: {total_quizzes_to_create}"
        preview_msg += f"\nTotal Questions to Use: {total_questions_to_use}"
        preview_msg += f"\n\nCategory Breakdown:"
        
        for data in preview_data:
            preview_msg += f"\n{data['category']}:"
            preview_msg += f"\n  - Unused Questions: {data['unused_questions']}"
            preview_msg += f"\n  - Quizzes to Fill: {data['quizzes_to_fill']}"
            preview_msg += f"\n  - Questions Needed to Fill: {data['questions_needed_to_fill']}"
            preview_msg += f"\n  - New Quizzes to Create: {data['new_quizzes_to_create']}"
            preview_msg += f"\n  - Questions for New Quizzes: {data['questions_for_new_quizzes']}"
            preview_msg += f"\n  - Starting Quiz Number: {data['starting_quiz_number']}"
        
        preview_msg += "\n\nDo you want to proceed with quiz creation? (y/n): "
        self.stdout.write(preview_msg)
        logger.info(preview_msg)
        
        # Get user confirmation
        try:
            response = input().lower()
            if response != 'y':
                abort_msg = "\nQuiz creation aborted by user."
                self.stdout.write(self.style.ERROR(abort_msg))
                logger.warning(abort_msg)
                return
        except KeyboardInterrupt:
            abort_msg = "\nQuiz creation aborted by user."
            self.stdout.write(self.style.ERROR(abort_msg))
            logger.warning(abort_msg)
            return
        
        # Proceed with quiz creation
        proceed_msg = "\nProceeding with quiz creation..."
        self.stdout.write(proceed_msg)
        logger.info(proceed_msg)
        
        total_quizzes_created = 0
        total_questions_used = 0
        category_summary = []

        for category in all_categories:
            # Get all questions for this category that aren't already in any quiz
            unused_questions = Question.objects.filter(
                category=category
            ).exclude(
                questions__isnull=False  # Exclude questions that are already in quizzes
            )
            
            unused_questions = list(unused_questions)
            num_unused = len(unused_questions)
            
            category_msg = f"\nProcessing {category.name} - {category.exam_type.name}: {num_unused} unused questions"
            self.stdout.write(category_msg)
            logger.info(category_msg)
            
            if num_unused == 0:
                continue
                
            # Shuffle the questions to ensure randomness
            random.shuffle(unused_questions)
            
            # First, fill existing quizzes that have fewer than 10 questions
            existing_quizzes = Quiz.objects.filter(category=category)
            questions_used = 0
            
            for quiz in existing_quizzes:
                current_questions = quiz.questions.count()
                if current_questions < 10 and unused_questions:
                    questions_needed = 10 - current_questions
                    questions_to_add = unused_questions[:questions_needed]
                    unused_questions = unused_questions[questions_needed:]
                    
                    for question in questions_to_add:
                        quiz.questions.add(question)
                        questions_used += 1
                    
                    fill_msg = f"Added {len(questions_to_add)} questions to {quiz.title}"
                    self.stdout.write(fill_msg)
                    logger.info(fill_msg)
            
            # Get the next quiz number for this category
            next_quiz_number = get_next_quiz_number(category)
            
            # Create new quizzes with remaining questions
            quizzes_created = 0
            
            while unused_questions:
                # Take up to 10 questions for this quiz
                quiz_questions = unused_questions[:10]
                unused_questions = unused_questions[10:]
                
                # Create a new quiz
                new_quiz = Quiz.objects.create(
                    title=f"{category.name}: Quiz {next_quiz_number + quizzes_created}",
                    category=category,
                    quiz_type=category.exam_type
                )
                
                # Add questions to the quiz
                for question in quiz_questions:
                    new_quiz.questions.add(question)
                    questions_used += 1
                
                quiz_msg = f"Created {new_quiz.title} with {len(quiz_questions)} questions"
                self.stdout.write(quiz_msg)
                logger.info(quiz_msg)
                
                quizzes_created += 1
                total_quizzes_created += 1
            
            total_questions_used += questions_used
            
            category_summary.append({
                'category': f"{category.name} - {category.exam_type.name}",
                'quizzes_created': quizzes_created,
                'questions_used': questions_used
            })
        
        # Print summary
        summary_msg = f"\nQuiz Creation Summary:"
        summary_msg += f"\nTotal New Quizzes Created: {total_quizzes_created}"
        summary_msg += f"\nTotal Questions Used: {total_questions_used}"
        summary_msg += f"\n\nCategory Breakdown:"
        
        for summary in category_summary:
            summary_msg += f"\n{summary['category']}:"
            summary_msg += f"\n  - New Quizzes Created: {summary['quizzes_created']}"
            summary_msg += f"\n  - Questions Used: {summary['questions_used']}"
        
        self.stdout.write(self.style.SUCCESS(summary_msg))
        logger.info(summary_msg) 