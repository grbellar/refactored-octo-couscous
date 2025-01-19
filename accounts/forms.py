from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('first_name', 'last_name', 'school', 'email', 'username',)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username',)


class MyCustomSignupForm(SignupForm):

    SCHOOL_CHOICES = [
        ('', 'Please select your school'),  # Placeholder option
        ('arizona', 'Arizona'),
        ('baylor_scott_and_white', 'Baylor Scott and White'),
        ('northern_kentucky', 'Northern Kentucky'),
        ('lawrence_tech', 'Lawrence Tech'),
        ('lipscomb', 'Lipscomb'),
        ('utah', 'Utah'),
        ('hofstra', 'Hofstra'),
        ('thomas_jefferson', 'Thomas Jefferson'),
        ('musc', 'MUSC'),
        ('msoe', 'MSOE'),
        ('texas_heart_institute', 'Texas Heart Institute'),
        ('vanderbilt', 'Vanderbilt'),
        ('upmc', 'UPMC'),
        ('cleveland_clinic', 'Cleveland Clinic'),
        ('suny', 'SUNY'),
        ('nebraska', 'Nebraska'),
        ('iowa', 'Iowa'),
        ('rush', 'Rush'),
        ('quinnipiac', 'Quinnipiac'),
        ('midwestern', 'Midwestern'),
        ('texas_health_science_center', 'Texas Health Science Center'),
        ('usc', 'USC'),
        ('other', 'Other'),
    ]

    def __init__(self, *args, **kwargs):
        super(MyCustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['first_name'] = forms.CharField(required=True)
        self.fields['last_name'] = forms.CharField(required=True)
        self.fields['school'] = forms.ChoiceField(
            choices=self.SCHOOL_CHOICES,
            required=True,
            error_messages={'required': 'Please select a valid school.'}
        )

    def save(self, request):

        # Call parent class's save() which returns a User object. I dont' need to explicity reassign 
        # first and last name because they are being saved by parent signup form (I think).
        user = super(MyCustomSignupForm, self).save(request)
        # Get the human-readable value of the selected school
        school_key = self.cleaned_data['school']
        school_display = dict(self.SCHOOL_CHOICES).get(school_key, school_key)
        user.school = school_display
        user.save()

        return user