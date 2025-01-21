from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe

# Register your models here.

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category')

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)

class ExplanationAdmin(admin.ModelAdmin):
    readonly_fields = ('question',)

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

admin.site.register(UserQuizAnswer, UserQuizAnswerAdmin)

class UserQuizStateAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        # Make all fields read-only
        return [field.name for field in self.model._meta.fields]

admin.site.register(UserQuizState, UserQuizStateAdmin)
class QuizAdmin(admin.ModelAdmin):
    filter_horizontal = ('questions',)
    readonly_fields = ('uuid',)
    list_display = ('title', 'category', 'uuid')

admin.site.register(Quiz, QuizAdmin)

