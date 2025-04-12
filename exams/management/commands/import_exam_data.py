import json
import logging
import os
import time
from django.core.management.base import BaseCommand
from exams.models import Category, Question, Choice, Explanation

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
os.makedirs('zlogs', exist_ok=True)

# Create file handler
file_handler = logging.FileHandler('zlogs/import_exam_data.log')
file_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(file_handler)

class Command(BaseCommand):
    help = 'Import exam questions, answers, and explanations from JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            'exam_type',
            type=str,
            help='The exam type to import (e.g., "Clinical Application", "Basic Science", etc.)',
        )

    def handle(self, *args, **options):
        exam_type = options['exam_type']
        
        # Get available exam types for better error messaging
        available_types = Category.objects.values_list('exam_type__name', flat=True).distinct()
        
        if not available_types:
            msg = "No exam types found in the database"
            self.stderr.write(self.style.ERROR(msg))
            logger.error(msg)
            return
            
        if exam_type not in available_types:
            msg = f"Invalid exam type: {exam_type}\nAvailable exam types: {', '.join(available_types)}"
            self.stderr.write(self.style.ERROR(msg))
            logger.error(msg)
            return
        
        # Build the query
        categories_query = Category.objects.filter(exam_type__name=exam_type)
        categories = categories_query.values_list('name', 'id', 'exam_type__name')
        
        if not categories:
            msg = f"No categories found for exam type: {exam_type}"
            self.stderr.write(self.style.ERROR(msg))
            logger.error(msg)
            return
        
        # Print categories for user verification
        success_msg = f"Found {len(categories)} categories for {exam_type}:"
        self.stdout.write(self.style.SUCCESS(success_msg))
        logger.info(success_msg)
        
        for category in categories:
            category_name, category_id, category_exam_type = category
            category_msg = f"{category_exam_type} - {category_name} ({category_id})"
            self.stdout.write(category_msg)
            logger.info(category_msg)
        
        # Ask for user confirmation before proceeding
        warning_msg = "\nPlease review the categories above. Do the ID's look correct? Press Enter to continue or Ctrl+C to abort..."
        self.stdout.write(self.style.WARNING(warning_msg))
        logger.warning(warning_msg)
        
        try:
            input()
        except KeyboardInterrupt:
            abort_msg = "\nImport aborted by user."
            self.stdout.write(self.style.ERROR(abort_msg))
            logger.warning(abort_msg)
            return
            
        start_msg = f"Approved. Starting data import for {exam_type} Categories..."
        time.sleep(2)
        self.stdout.write(start_msg)
        logger.info(start_msg)
        
        import_summary = [] # Stores a tuple like this, ("Clinical Application - Anatomy and Physiology (ID: 1)", 56)
        total_questions_imported = 0


        for category in categories:
            question_import_counter = 0
            category_name, category_id, category_exam_type = category
            process_msg = f"Processing {category_exam_type} - {category_name} ID: {category_id}"
            self.stdout.write(process_msg)
            logger.info(process_msg)
            
            try:
                if exam_type == "Clinical Application":
                    translation = "CAPE"
                elif exam_type == "Basic Science":
                    translation = "PBSE"
                else:
                    translation = exam_type
                with open(f"zdata-to-import/{translation} - {category_name} - BLACK - DONE.json", 'r') as file:
                    question_list = json.load(file)
                
                found_msg = f"Found {len(question_list)} questions for {category_name}"
                self.stdout.write(found_msg)
                logger.info(found_msg)
                
                for quiz_question in question_list:
                    category_from_db = Category.objects.get(id=category_id)
                    new_question = Question.objects.create(
                        text=quiz_question["text"],
                        category=category_from_db
                    )
                    question_msg = f"Added question {quiz_question['question_number']}: {new_question.text}"
                    question_import_counter += 1
                    self.stdout.write(question_msg)
                    logger.info(question_msg)
                    
                    for choice in quiz_question["choices"]:
                        choice = Choice.objects.create(
                            question=new_question,
                            text=choice["text"],
                            is_correct=choice["is_correct"]
                        )
                        choice_msg = f"Choice: {choice.text} - {choice.is_correct}"
                        self.stdout.write(choice_msg)
                        logger.info(choice_msg)
                    
                    explanation = Explanation.objects.create(
                        question=new_question,
                        text=quiz_question["explanation"],
                        sources=quiz_question["sources"]
                    )
                    explanation_msg = f"Explanation: {explanation.text}"
                    sources_msg = f"Sources: {explanation.sources}"
                    self.stdout.write(explanation_msg)
                    self.stdout.write(sources_msg)
                    logger.info(explanation_msg)
                    logger.info(sources_msg)
                
                import_summary.append((f"\n{category_exam_type} - {category_name} - ID: {category_id}", f"({question_import_counter})"))
                total_questions_imported += question_import_counter
            except FileNotFoundError:
                error_msg = f"Warning: Could not find file for category {category_name}"
                self.stderr.write(error_msg)
                logger.warning(error_msg)
                continue
            except Exception as e:
                error_msg = f"Error processing category {category_name}: {str(e)}"
                self.stderr.write(error_msg)
                logger.error(error_msg)
                continue
        
        # TODO: Add better logging for files that fail. Currently they fail silently and it acts like they all completed even though there might be fine now found errors.
        success_msg = f"Data import completed successfully! Total questions imported {total_questions_imported}: "
        for tup in import_summary:
            success_msg += f"{tup[0]} - {tup[1]}, "
        self.stdout.write(self.style.SUCCESS(success_msg))
        logger.info(success_msg) 