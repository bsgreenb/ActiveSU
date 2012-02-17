__author__ = 'rui'

from django import forms
from django.contrib.auth.models import User

from activity.models import *

from bootstrap.forms import BootstrapForm, Fieldset





class RegistrationForm(BootstrapForm):
    class Meta:
        layout = {
            Fieldset('Register', 'email', 'password1', 'password2')
        }

    # we use prefix of the email as username
    email = forms.EmailField(label=u'Stanford School Email', error_messages={'required':'a', 'invalid':''})
    password1 = forms.CharField(label=u'Password', widget=forms.PasswordInput(), error_messages={'required':'d', 'invalid':''})
    password2 = forms.CharField(label=u'Confirm Password', widget=forms.PasswordInput(), error_messages={'required':'e', 'invalid':''})

    def clean_email(self):
        school_email_suffix = self.cleaned_data['email'].split('@')[-1]
        if school_email_suffix == 'stanford.edu':
            return self.cleaned_data['email']
        raise forms.ValidationError('Please provide your stanford email address.')


    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']

            if password1 == password2:
                return password2
        raise forms.ValidationError('Passwords do not match')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

class TextPostForm(forms.Form):
    content = forms.CharField(max_length=500)
    activity_page = forms.IntegerField(min_value=1)

class EventPostForm(forms.Form):
    title = forms.CharField(max_length=100)
    start_date = forms.DateTimeField()
    start_time = forms.IntegerField()
    end_date = forms.DateTimeField(required = False)
    end_time = forms.IntegerField(required = False)
    where = forms.CharField(max_length = 200)
    description = forms.CharField(max_length = 500, required=False)
