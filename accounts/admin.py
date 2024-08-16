from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from exams.admin import UserExamState

class UserExamStateInline(admin.StackedInline):
    model = UserExamState
    extra = 0

    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        # Make all fields in the UserExamState inline read-only
        return [field.name for field in self.model._meta.fields]


class CustomUserAdmin(UserAdmin):
    inlines = [UserExamStateInline]

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    list_display = ['email', 'first_name', 'last_name', 'school', 'date_joined']
    readonly_fields = ['uuid', 'date_joined', 'last_login']

    fieldsets = [
        (
            'User Information',
            {
                "fields": ["first_name", "last_name", "email", "school", "date_joined", "uuid", "password"]
            }
        ),
        (
            'Paid Status',
            {
                "fields": ["has_paid", "exam_tokens"]
            }
        ),
    ]

admin.site.register(CustomUser, CustomUserAdmin)