from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Exam)
admin.site.register(Choice)
admin.site.register(Category)


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
