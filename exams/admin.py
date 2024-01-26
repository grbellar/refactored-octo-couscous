from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Exam)
admin.site.register(Choice)


# ExamType editing
class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1


class ExamTypeAdmin(admin.ModelAdmin):
    inlines = [CategoryInline]


admin.site.register(ExamType, ExamTypeAdmin)


# Category editing
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    inlines = QuestionInline


admin.site.register(Category)


class ExamAdmin(admin.ModelAdmin):
    filter_horizontal = ('questions')


class ChoiceInline(admin.StackedInline):
    model = Choice

    def get_extra(self, request, obj=None, **kwargs):
        extra = 4
        if obj:
            return extra - obj.choices.all().count()
        return extra



class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]


admin.site.register(Question, QuestionAdmin)
