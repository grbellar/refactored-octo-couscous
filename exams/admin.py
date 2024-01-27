from django.contrib import admin
from django.forms import ModelChoiceField
from django.http.request import HttpRequest
from .models import *

# Register your models here.
admin.site.register(Exam)
admin.site.register(Choice)
admin.site.register(UserAnswer)


# ExamType editing
class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class ExamTypeAdmin(admin.ModelAdmin):
    inlines = [CategoryInline]


admin.site.register(ExamType, ExamTypeAdmin)


# Category editing
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0

    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False


class CategoryAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ['name', 'exam_type']


admin.site.register(Category, CategoryAdmin)


class ExamAdmin(admin.ModelAdmin):
    filter_horizontal = ('questions')
    


class ChoiceInline(admin.StackedInline):
    model = Choice

    def get_extra(self, request, obj=None, **kwargs):
        extra = 4
        if obj:
            return extra - obj.choices.all().count()
        return extra


class CategoryChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        # Check if exam_type exists for the category
        if obj.exam_type:
            return f"{obj.exam_type.name} - {obj.name}"
        else:
            return f"No ExamType set - {obj.name}"


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['text', 'id']


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            return CategoryChoiceField(queryset=Category.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Question, QuestionAdmin)

# EXAM STATES
class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0

    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False


class UserExamStateAdmin(admin.ModelAdmin):
    inlines = [UserAnswerInline]


admin.site.register(UserExamState, UserExamStateAdmin)
