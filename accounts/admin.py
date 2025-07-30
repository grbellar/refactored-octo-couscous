from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from exams.admin import UserExamState
from allauth.account.models import EmailAddress

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
    
    list_display = ['email', 'first_name', 'last_name', 'school', 'date_joined', 'has_paid_v2', 'legacy_has_paid_token', 'email_verified', 'is_question_editor']
    readonly_fields = ['uuid', 'date_joined', 'last_login', 'email_verified', 'is_question_editor']
    list_filter = ('is_staff', 'is_active', 'groups')

    fieldsets = [
        (
            'User Information',
            {
                "fields": ["first_name", "last_name", "username", "email", "school", "date_joined", "uuid", "password", "email_verified"]
            }
        ),
        (
            'Permissions',
            {
                "fields": ["is_active", "is_staff", "is_superuser", "groups", "user_permissions", "is_question_editor"]
            }
        ),
        (
            'Paid Status',
            {
                "fields": ["has_paid_v2"]
            }
        ),
    ]
    
    def is_question_editor(self, obj):
        return obj.groups.filter(name='Question Editor').exists()
    is_question_editor.boolean = True
    is_question_editor.short_description = "Question Editor"
    
    def email_verified(self, obj):
        email_address = EmailAddress.objects.filter(user=obj, email=obj.email).first()
        if email_address:
            return email_address.verified
        return False
    
    email_verified.boolean = True  # Display as a checkbox icon
    email_verified.short_description = "Email Verified"
    email_verified.admin_order_field = 'emailaddress__verified'  # Make column sortable

admin.site.register(CustomUser, CustomUserAdmin)