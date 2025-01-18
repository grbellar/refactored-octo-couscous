from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(UserQuizAnswer)
admin.site.register(UserQuizState)
class QuizAdmin(admin.ModelAdmin):
    filter_horizontal = ('questions',)
    readonly_fields = ('uuid',)
    list_display = ('title', 'uuid')

admin.site.register(Quiz, QuizAdmin)

