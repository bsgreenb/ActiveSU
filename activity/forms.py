import re

from django import forms
from django.contrib.auth.models import User

from bootstrap.forms import BootstrapForm, Fieldset

from activity.models import *
from activity.library.send_mail import send_registration_confirmation


VALID_EMAIL_SUFFIX = ('stanford.edu')


class RegistrationForm(BootstrapForm):
    class Meta:
        layout = {
            Fieldset('Register', 'username', 'email', 'password1', 'password2')
        }

    # we use prefix of the email as username
    username = forms.CharField(label=u'Username', error_messages={'required':'The username is required', 'invalid':'The username you entered is invalid'})
    email = forms.EmailField(label=u'Stanford Email', error_messages={'required':'Please provide your stanford.edu school email', 'invalid':'The email you entered is invalid'})
    password1 = forms.CharField(label=u'Password', widget=forms.PasswordInput(), error_messages={'required':'Please provide a password', 'invalid':'The password you entered is invalid'})
    password2 = forms.CharField(label=u'Confirm Password', widget=forms.PasswordInput(), error_messages={'required':'Please provide the password confirmation', 'invalid':'The confirmation password you provided is invalid.'})

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
                raise forms.ValidationError('This email is already registered and activated.')
            else:
                send_registration_confirmation(user)
                raise forms.ValidationError("This email is already registered. We've e-mailed you confirmation code to the e-mail address you submitted.")
        except User.DoesNotExist:
            school_email_suffix = self.cleaned_data['email'].split('@')[-1]
            
            
            
            if school_email_suffix in VALID_EMAIL_SUFFIX:
                return self.cleaned_data['email']
            raise forms.ValidationError('Please provide your iu.edu email address')


    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']

            if password1 == password2:
                return password2
        raise forms.ValidationError('The confirmation password doesn\'t match')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

class TextPostForm(forms.Form):
    content = forms.CharField(max_length=500, error_messages={'required':'Please provide a message', 'invalid':'Please limit the message to 500 characters'})

class EventPostForm(forms.Form):
    title = forms.CharField(max_length=100, error_messages={'required':'Activity title ("What") is required', 'invalid':'Please limit the title to less than 100 characters'})
    where = forms.CharField(max_length = 200, error_messages={'required':'The location ("Where") is required', 'invalid':'The provided location ("Where") is invalid'})
    start_date = forms.DateTimeField(error_messages={'required':'Start date is required', 'invalid':'Start date is invalid'})
    start_time = forms.IntegerField(error_messages={'required':'Start time is required', 'invalid':'Start time is invalid'})
    end_date = forms.DateTimeField(required = False)
    end_time = forms.IntegerField(required = False)
    description = forms.CharField(max_length = 500, required=False, error_messages={'invalid':'Please limit the event description to 500 characters'})

class SendMessageForm(forms.Form):
    post_id = forms.IntegerField()
    post_message = forms.CharField(max_length = 500)


