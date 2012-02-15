__author__ = 'rui'

from django import forms
from django.contrib.auth.models import User

from activity.models import *

from bootstrap.forms import BootstrapForm, Fieldset





class RegistrationForm(BootstrapForm):
    class Meta:
        layout = {
            Fieldset('Register', 'email', 'first_name', 'last_name', 'password1', 'password2')
        }

    # we use prefix of the email as username
    email = forms.EmailField(label=u'School Email', error_messages={'required':'a', 'invalid':''})
    first_name = forms.CharField(label=u'First Name', max_length = 30, error_messages={'required':'b', 'invalid':''})
    last_name = forms.CharField(label=u'Last Name', max_length = 30, error_messages={'required':'c', 'invalid':''})
    password1 = forms.CharField(label=u'Password', widget=forms.PasswordInput(), error_messages={'required':'d', 'invalid':''})
    password2 = forms.CharField(label=u'Confirm Password', widget=forms.PasswordInput(), error_messages={'required':'e', 'invalid':''})

    def clean_email(self):
        school_email_suffix = self.cleaned_data['email'].split('@')[-1]
        if school_email_suffix == 'stanford':
            return self.cleaned_data['email']
        raise forms.ValidationError('Please provide your stanford email address.')


    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']

            if password1 == password2:
                return password2
        raise forms.ValidationError('Passwords do not match')