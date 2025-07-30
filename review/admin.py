from django.contrib import admin
from .models import Answer, Explanation, Question, Quiz, UserQuizAnswer, UserQuizState
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

# Register your models here.

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('choice_count', 'answer_link')
    can_delete = False

    def answer_link(self, obj):
        if obj.id:
            return mark_safe(f'<a href="/admin/review/answer/{obj.id}/change/">View Answer</a>')
        return "-"
    
    answer_link.short_description = "Link to Answer"

class ExplanationInline(admin.TabularInline):
    model = Explanation
    max_num = 1
    can_delete = False

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'flagged', 'flag_count', 'flag_summary')
    list_filter = ('category', 'flagged')
    readonly_fields = ('flag_count', 'flag_details', 'clear_flags_button')
    inlines = [AnswerInline, ExplanationInline]
    search_fields = ('text',)
    list_per_page = 50
    exclude = ('flag_reasons',)
    
    def has_module_permission(self, request):
        """Allow access if user is superuser or in Question Editor group"""
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Question Editor').exists()
    
    def has_view_permission(self, request, obj=None):
        """Allow view if user has question view permission"""
        return request.user.has_perm('review.view_question')
    
    def has_add_permission(self, request):
        """Allow add if user has question add permission"""
        return request.user.has_perm('review.add_question')
    
    def has_change_permission(self, request, obj=None):
        """Allow change if user has question change permission"""
        return request.user.has_perm('review.change_question')
    
    def has_delete_permission(self, request, obj=None):
        """Allow delete if user has question delete permission"""
        return request.user.has_perm('review.delete_question')
    
    def clear_flags_button(self, obj):
        if obj.flagged:
            return mark_safe(
                f'<a href="/admin/review/question/{obj.id}/clear-flags/" '
                f'class="button" style="background: #008000; color: white; padding: 8px 12px; '
                f'text-decoration: none; border-radius: 4px;">Mark as fixed</a>'
            )
        return "No flags to clear"
    clear_flags_button.short_description = "Actions"
    
    def flag_summary(self, obj):
        if obj.flagged and obj.flag_reasons:
            return f"{len(obj.flag_reasons)} flag(s)"
        return "No flags"
    flag_summary.short_description = "Flags"
    
    def flag_details(self, obj):
        if obj.flagged and obj.flag_reasons:
            details = []
            for flag in obj.flag_reasons:
                detail = f"<strong>{flag.get('username', 'Unknown')}</strong>: {flag.get('reason', 'No reason')}"
                if flag.get('reason_explained'):
                    detail += f"<br><em>Explanation: {flag.get('reason_explained')}</em>"
                details.append(detail)
            return mark_safe("<br><br>".join(details))
        return "No flags"
    flag_details.short_description = "Flag Details"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:question_id>/clear-flags/',
                self.admin_site.admin_view(self.clear_flags_view),
                name='question-clear-flags',
            ),
        ]
        return custom_urls + urls
    
    def clear_flags_view(self, request, question_id):
        from django.shortcuts import redirect
        from django.contrib import messages
        
        # Check permission
        if not request.user.has_perm('review.change_question'):
            raise PermissionDenied("You don't have permission to clear flags")
        
        try:
            question = Question.objects.get(id=question_id)
            if question.flagged:
                question.flag_reasons = []
                question.flagged = False
                question.save()
                messages.success(request, f"Flags cleared for question: {question.text[:50]}...")
            else:
                messages.warning(request, "This question has no flags to clear.")
        except Question.DoesNotExist:
            messages.error(request, "Question not found.")
        
        return redirect(f'/admin/review/question/{question_id}/change/')

admin.site.register(Question, QuestionAdmin)

class AnswerAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        """Allow access if user is superuser or in Question Editor group"""
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Question Editor').exists()

admin.site.register(Answer, AnswerAdmin)

class ExplanationAdmin(admin.ModelAdmin):
    readonly_fields = ('question',)
    
    def has_module_permission(self, request):
        """Allow access if user is superuser or in Question Editor group"""
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Question Editor').exists()

admin.site.register(Explanation, ExplanationAdmin)

class UserQuizAnswerAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        # Make all fields read-only
        fields = [field.name for field in self.model._meta.fields]
        if obj:  # Only add explanation when editing an object
            fields.append('question_explanation')
        return fields
        
    def question_explanation(self, obj):
        if obj.question and hasattr(obj.question, 'explanation'):
            explanation = obj.question.explanation
            # Return a link to the explanation in the admin
            return mark_safe(f'<a href="/admin/review/explanation/{explanation.id}/change/">{explanation}</a>')
        return "No explanation available"
    
    question_explanation.short_description = "Explanation"
    
    list_display = ('question',)
    
    def has_module_permission(self, request):
        """Only superusers can access user quiz answers"""
        return request.user.is_superuser

admin.site.register(UserQuizAnswer, UserQuizAnswerAdmin)

class UserQuizStateAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        # Make all fields read-only
        return [field.name for field in self.model._meta.fields]
    
    def has_module_permission(self, request):
        """Only superusers can access user quiz states"""
        return request.user.is_superuser

admin.site.register(UserQuizState, UserQuizStateAdmin)

class QuizAdmin(admin.ModelAdmin):
    filter_horizontal = ('questions',)
    readonly_fields = ('uuid',)
    list_display = ('title', 'category', 'uuid')
    list_filter = ('category',)
    
    def has_module_permission(self, request):
        """Only superusers can access quizzes"""
        return request.user.is_superuser

admin.site.register(Quiz, QuizAdmin)

