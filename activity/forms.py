from activity.models import *
from django import forms
from django.contrib.auth.models import User

from bootstrap.forms import BootstrapForm, Fieldset

from activity.library.send_mail import send_registration_confirmation


class RegistrationForm(BootstrapForm):
    class Meta:
        layout = {
            Fieldset('Register', 'username', 'email', 'password1', 'password2')
        }

    # we use prefix of the email as username
    username = forms.CharField(label=u'Username', error_messages={'required':'', 'invalid':''})
    email = forms.EmailField(label=u'Stanford School Email', error_messages={'required':'please provide your stanford school email', 'invalid':'the email is invalid'})
    password1 = forms.CharField(label=u'Password', widget=forms.PasswordInput(), error_messages={'required':'please provide the password', 'invalid':'the password is invalid'})
    password2 = forms.CharField(label=u'Confirm Password', widget=forms.PasswordInput(), error_messages={'required':'please provide the confirm password', 'invalid':'the confirm password is invalid'})

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Usernames can only contain letters, numbers, and underscores.')
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('An account with this username is already registered.')

    def clean_email(self):
        try:
            user = User.objects.select_related().get(email = self.cleaned_data['email'])
            if user.is_active:
                raise forms.ValidationError('this email is already registered and activated.')
            else:
                send_registration_confirmation(user)
                raise forms.ValidationError("this email is already registered. We've e-mailed you confirmation code to the e-mail address you submitted.")
        except User.DoesNotExist:
            school_email_suffix = self.cleaned_data['email'].split('@')[-1]
            if school_email_suffix == 'stanford.edu':
                return self.cleaned_data['email']
            raise forms.ValidationError('please provide your stanford email address.')


    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']

            if password1 == password2:
                return password2
        raise forms.ValidationError('passwords do not match')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

class TextPostForm(forms.Form):
    content = forms.CharField(max_length=500, error_messages={'required':'please provide the message', 'invalid':'please limit the message in 500 characters'})
    activity_page = forms.IntegerField(min_value=1, error_messages={'required':'please provide the page number'})

class EventPostForm(forms.Form):
    title = forms.CharField(max_length=100, error_messages={'required':'title is required', 'invalid':'please limit the title in 100 characters'})
    where = forms.CharField(max_length = 200, error_messages={'required':'where is required', 'invalid':'where is invalid'})
    start_date = forms.DateTimeField(error_messages={'required':'start date is required', 'invalid':'start date is invalid'})
    start_time = forms.IntegerField(error_messages={'required':'start time is required', 'invalid':'start time is invalid'})
    end_date = forms.DateTimeField(required = False)
    end_time = forms.IntegerField(required = False)
    description = forms.CharField(max_length = 500, required=False, error_messages={'required':'title is required', 'invalid':'please limit the description in 500 characters'})
