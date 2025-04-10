from django.contrib import admin
from .models import Answer, Explanation, Question, QuestionFlag, Quiz, UserQuizAnswer, UserQuizState
from django.utils.safestring import mark_safe

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
    list_display = ('text', 'category')
    list_filter = ('category',)
    readonly_fields = ('category', 'flag_reasons')
    inlines = [AnswerInline, ExplanationInline]
    exclude = ('flagged', 'flag_count')

    def flag_reasons(self, obj):
        flags = obj.questionflag_set.all()
        if not flags:
            return "No flags"
        
        reasons = [f"- {flag.reason} (by {flag.user})" for flag in flags]
        return mark_safe("<br>".join(reasons))
    
    flag_reasons.short_description = "Flag Reasons"

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
    list_filter = ('category',)

admin.site.register(Quiz, QuizAdmin)

class QuestionFlagAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Only apply to existing objects
            return ('reason', 'question', 'user', 'created_at', 'reason_explained')
        return ('user', 'created_at')  # Allow question selection on creation
    
    def count(self, obj):
        print("In count:", obj)
        return obj.question.questionflag_set.count()

    
    count.short_description = "Count"
    # count.admin_order_field = 'question__flag_count'  # Make column sortable
    # If this doesn't work try adding flag_count back to the question model. Don't exclude it. Django might be struggling to query the data because of that.
    
    list_display = ('question', 'reason', 'user', 'created_at', 'count')
    list_filter = ('reason',)

admin.site.register(QuestionFlag, QuestionFlagAdmin)

