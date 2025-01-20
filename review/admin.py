from django.contrib import admin
from .models import *

# Register your models here.

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category')

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(UserQuizAnswer)
admin.site.register(UserQuizState)
class QuizAdmin(admin.ModelAdmin):
    filter_horizontal = ('questions',)
    readonly_fields = ('uuid',)
    list_display = ('title', 'category', 'uuid')

admin.site.register(Quiz, QuizAdmin)

