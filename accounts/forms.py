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

    def __init__(self, *args, **kwargs):
        super(MyCustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['first_name'] = forms.CharField(required=True)
        self.fields['last_name'] = forms.CharField(required=True)
        self.fields['school'] = forms.CharField(required=True)

    def save(self, request):

        # Call parent class's save() which returns a User object. I dont' need to explicity reassign 
        # first and last name because they are being saved by parent signup form (I think).
        user = super(MyCustomSignupForm, self).save(request)
        user.school = self.cleaned_data['school']
        user.save()  

        return user