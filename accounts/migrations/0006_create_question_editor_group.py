# Generated manually for question editor role setup
from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def create_question_editor_group(apps, schema_editor):
    """
    Create Question Editor group with permissions to manage review questions
    """
    # Get the Question model
    Question = apps.get_model('review', 'Question')
    Answer = apps.get_model('review', 'Answer')
    Explanation = apps.get_model('review', 'Explanation')
    
    # Create or get the Question Editor group
    group, created = Group.objects.get_or_create(name='Question Editor')
    
    if created:
        print("Created Question Editor group")
    else:
        print("Question Editor group already exists")
    
    # Get content types
    question_ct = ContentType.objects.get_for_model(Question)
    answer_ct = ContentType.objects.get_for_model(Answer)
    explanation_ct = ContentType.objects.get_for_model(Explanation)
    
    # Define permissions to add
    permissions_to_add = [
        # Question permissions
        ('view_question', question_ct),
        ('add_question', question_ct),
        ('change_question', question_ct),
        ('delete_question', question_ct),
        
        # Answer permissions (since they're inline with questions)
        ('view_answer', answer_ct),
        ('add_answer', answer_ct),
        ('change_answer', answer_ct),
        ('delete_answer', answer_ct),
        
        # Explanation permissions (since they're inline with questions)
        ('view_explanation', explanation_ct),
        ('add_explanation', explanation_ct),
        ('change_explanation', explanation_ct),
        ('delete_explanation', explanation_ct),
    ]
    
    # Add permissions to the group
    for perm_codename, content_type in permissions_to_add:
        try:
            permission = Permission.objects.get(
                codename=perm_codename,
                content_type=content_type
            )
            group.permissions.add(permission)
            print(f"Added permission: {perm_codename}")
        except Permission.DoesNotExist:
            print(f"Permission {perm_codename} not found - skipping")
    
    print(f"Question Editor group setup complete with {group.permissions.count()} permissions")


def remove_question_editor_group(apps, schema_editor):
    """
    Remove the Question Editor group
    """
    try:
        group = Group.objects.get(name='Question Editor')
        group.delete()
        print("Removed Question Editor group")
    except Group.DoesNotExist:
        print("Question Editor group not found")


class Migration(migrations.Migration):
    
    dependencies = [
        ('accounts', '0005_rename_has_paid_customuser_legacy_has_paid_token_and_more'),
        ('review', '0012_remove_question_flag_count_question_flag_reasons_and_more'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]
    
    operations = [
        migrations.RunPython(
            create_question_editor_group,
            remove_question_editor_group,
        ),
    ] 