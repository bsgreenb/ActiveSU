import datetime
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail
from django.test import Client

from activity.models import *
from activity.forms import *

FAKE_USERNAME = 'fakeuser'
FAKE_EMAIL = 'fakeuser@stanford.edu'
FAKE_PASSWORD = 'fakepassword'
FAKE_URL = 'thisisafakeurl'


#TODO
#unittest for get_posts_and_comments
#unittest for get_future_events_and_comments



def create_and_login_user():

    client = Client()
    
    user = User.objects.create_user(FAKE_USERNAME, FAKE_EMAIL, FAKE_PASSWORD)
    user.is_active = True
    user.save()
    
    login_successful = client.login(username=user.username, password=FAKE_PASSWORD)
    
    return user, client

# form #

class Test_RegistrationForm(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.data = {
            'username':FAKE_USERNAME,
            'email':FAKE_EMAIL,
            'password1':FAKE_PASSWORD,
            'password2': FAKE_PASSWORD
            }

    def test_valid_case(self):
        self.assertTrue(RegistrationForm(self.data).is_valid())

    def test_invalid_cases(self):
        user = User.objects.all()[0]
        existing_username = user.username
        existing_email = user.email

        cases = {
            # cover clean_password2, clean_username and clean_email casess, and no school eamil cases
            'password2':'mopyard111',
            'username':existing_username,
            'email':existing_email,
            'not_stanford_email':'test@cc.edu'
        }

        for case in cases:
            if case == 'password2':
                self.data['password2'] = cases['password2']
            elif case == 'username':
                self.data['username'] = cases['username']
            elif case == 'email':
                self.data['email'] = cases['email']
            elif case == 'not_stanford_email':
                self.data['email'] = cases['not_stanford_email']

        f = RegistrationForm(self.data)
        self.assertFalse(f.is_valid())

# view #
class Test_Logout_Page(TestCase):
    fixtures = ['test_data.json']

    def test_logout_page(self):
        # requirement 1. a logged in user can be logged out.
        user = User.objects.create_user(FAKE_USERNAME, FAKE_EMAIL, FAKE_PASSWORD)

        login = self.client.login(username = user.username, password=FAKE_PASSWORD) # can't use user.password because it's hashed

        self.assertTrue(login) # logged in user.
        response = self.client.get(reverse('logout'), follow=True)
        self.assertTemplateUsed(response, 'main_page.html')


class Test_Register_Page(TestCase):

    fixtures = ['test_data.json']
    
    def setUp(self):
        self.data = {'username':FAKE_USERNAME, 'password1':FAKE_PASSWORD, 'password2':'mopyard2', 'email':FAKE_EMAIL} # it's invalid data. the password is different

    def test_get(self):
        response = self.client.get(reverse('register'))
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_post_invalid_data(self):
        response = self.client.post(reverse('register'), self.data)
        self.assertTemplateUsed(response, 'registration/register.html') # invalid data. no need to test out all invalid cases since I already checked them at Test_Register_Form

    def test_post_valid_data(self):
        self.data['password2'] = FAKE_PASSWORD # now, the data is valid
        response = self.client.post(reverse('register'), self.data, follow=True)
        last_user = User.objects.all().order_by('-date_joined')[0]
        self.assertEqual(last_user.username, self.data['username'])
        self.assertEqual(last_user.email, self.data['email'])
        self.assertFalse(last_user.is_active)
        
        profile = last_user.get_profile()
        self.assertEqual(len(profile.confirmation_code), 33)
        self.assertEqual(len(profile.unsubscribe_code), 33)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Welcome to ' + settings.SITE_NAME)
        
        self.assertTemplateUsed(response, 'registration/register_confirm.html')
        
class Test_Confirm(TestCase):
    fixtures = ['test_data.json']
    
    def setUp(self):
        self.users = User.objects.all()
        
    def test_valid_confirm(self):
        for user in self.users:
            response = self.client.get(reverse('register_success', kwargs={'confirmation_code' : user.get_profile().confirmation_code, 'username': user.username}))
            
            updated_user = User.objects.get(username = user.username)
            
            self.assertTrue(updated_user.is_active)
            self.assertTemplateUsed(response, 'registration/register_confirm_success.html')
            self.assertContains(response, 'You successfully activated your account')
            
    def test_invalid_confirm_code(self):                
        for user in self.users:
            user.is_active = False
            user.save()
        
            confirmation_code = user.get_profile().confirmation_code[:-5] + 'kkkpq'
            response = self.client.get(reverse('register_success', kwargs={'confirmation_code' : confirmation_code, 'username': user.username}))
            updated_user = User.objects.get(username = user.username)
            self.assertFalse(updated_user.is_active)
            self.assertTemplateUsed(response, 'registration/register_confirm_success.html')
            self.assertContains(response, 'Sorry')
        
        
    def test_invalid_user(self):
        user = self.users[0]
        response = self.client.get(reverse('register_success', kwargs={'confirmation_code' : user.get_profile().confirmation_code, 'username': FAKE_USERNAME}))
        self.assertRedirects(response, reverse('register'))
        
class Test_Unsubscribe_Page(TestCase):
    fixtures = ['test_data.json']
    
    def setUp(self):
        self.users = User.objects.all()
        
    def test_valid_unsubscribe(self):
        for user in self.users:
            
            response = self.client.get(reverse('unsubscribe_page', kwargs={'username': user.username, 'unsubscribe_code':user.get_profile().unsubscribe_code}))
            
            self.assertTrue(user.get_profile().subscribe)
            self.assertContains(response, 'You successfully unsubscribed the account', status_code = 200)
            
    def test_invalid_username(self):
        user = self.users[0]
        response = self.client.get(reverse('unsubscribe_page', kwargs={'username': FAKE_USERNAME, 'unsubscribe_code':user.get_profile().unsubscribe_code}))
        
        self.assertContains(response, 'match any account', status_code = 200)
        
        
    def test_invalid_unsubscribe(self):
        for user in self.users:
            unsubscribe_code = user.get_profile().unsubscribe_code[:-5] + 'zzzjk'
            response = self.client.get(reverse('unsubscribe_page', kwargs={'username': user.username, 'unsubscribe_code':unsubscribe_code}))
            self.assertContains(response, "subscribe your account", status_code = 200)
        
class Test_Main_Page(TestCase):
    fixtures = ['test_data.json']
    def test_main_page(self):
        response = self.client.get(reverse('main_page'))
        self.assertTemplateUsed(response, 'main_page.html')
    

class Test_Activity_Page(TestCase):
    fixtures = ['test_data.json']
    
    #requirement 1. if the url code is invalid, redirect to main page
    #requirement 2. if the user is authenticated, create the user to this activity page

    def setUp(self):
        self.created_user, self.client = create_and_login_user()
        self.users = User.objects.all()
        self.activity_page = Activity_Page.objects.all()[0]
        
    def test_create_user_for_activity_page(self):
        response = self.client.post(reverse('activity_page', args=[self.activity_page.url_code]))
        
        self.assertIsNotNone(Activity_Page_User.objects.get(user = self.created_user))
        
    def test_invalid_url(self):
        response = self.client.post(reverse('activity_page', args=[FAKE_URL]))
        self.assertRedirects(response, reverse('main_page'))
    
    def test_valid_url(self):
        url = Activity_Page.objects.all()[0].url_code
        response = self.client.post(reverse('activity_page', args=[url]))
        self.assertTemplateUsed(response, 'activity_page.html')
    
class Test_Message_To_Post(TestCase):
    fixtures = ['test_data.json']
    
    def setUp(self):
        self.created_user, self.client = create_and_login_user()
        
    def test_message_to_post(self):
        post = Post.objects.filter(activity_page__show_email=True)[0]
        post_data = {'post_id': post.id, 'post_message': 'hello, I want to meet for tennis'}
        response = self.client.post(reverse('send_message_to_post'), post_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'You got a message from ActiveSU')
        self.assertEqual(mail.outbox[0].from_email, self.created_user.email)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertEqual(mail.outbox[0].to[0], post.user.email)
        self.assertContains(response, 'OK')
        
    def test_invalid_post(self):
        post = Post.objects.filter(activity_page__show_email=False)[0]
        post_data = {'post_id': post.id, 'post_message': 'hello, I want to meet for tennis'}
        response = self.client.post(reverse('send_message_to_post'), post_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, 'this page doesn\'t support message feature')
        
        post_data['post_id'] = 'zzzz'
        response = self.client.post(reverse('send_message_to_post'), post_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, 'the message is invalid')

        #post = Post.objects.filter(activity_page__show_email=True)[0]
        
        #post_data = {'post_id':post.id, 'post_message':'hello, i want to meet for tennsi'}
        #response = self.client.post(reverse('send_message_to_post'), post_data)
        
        #self.assertContains(response, 'invalid request')
        
class Test_Submit_Comment(TestCase):

    fixtures = ['test_data.json']
    # requirement 1. the post data is invalid. return a json that contains {'result':'invalid'}
    # requirement 2. when valid, return a json result and the email is not sending to itself.

    def setUp(self):
        self.created_user, self.client = create_and_login_user()
        self.post = Post.objects.all()[0]
        self.data = {'post':self.post.id, 'content':'this is a comment'}

    def test_invalid_post(self):
        self.data['post'] = -2
        response = self.client.post(reverse('post_comment'), self.data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, 'invalid')
        
    def test_submit_comment(self):
        response = self.client.post(reverse('post_comment'), self.data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        last_comment = Comment.objects.all().order_by('-comment_time')[0]
        self.assertEqual(last_comment.content, self.data['content'])
        self.assertEqual(last_comment.post, self.post)
        self.assertContains(response, 'OK')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'You got a message from ActiveSU')
        self.assertEqual(mail.outbox[0].from_email, self.created_user.email)
        for receiver_email in mail.outbox[0].to:
            self.assertNotEqual(receiver_email, self.created_user.email) # not send to himself.
        self.assertContains(response, 'OK')
             
             
             
class Test_Submit_Text_Post(TestCase):
    fixtures = ['test_data.json']
    
    def setUp(self):
        self.created_user, self.client = create_and_login_user()
        self.activity_page = Activity_Page.objects.get(pk=1)
        self.data = {'content':'hello, i want to play basketball with someone', 'activity_page':self.activity_page.id}
        
    def test_submit_text_post(self):
        response = self.client.post(reverse('post_message'), self.data)
        last_text_post = Post.objects.all().order_by('-post_time')[0].text_post
        self.assertEqual(last_text_post.content, self.data['content'])
        self.assertRedirects(response, reverse('activity_page', args=[self.activity_page.url_code]))
        
class Test_Submit_Event_Post(TestCase):
    fixtures = ['test_data.json']
    def setUp(self):
        self.created_user, self.client = create_and_login_user()
        self.activity_page = Activity_Page.objects.get(pk=1)
    def test_submit_event_post(self):
        data = {
            'activity_page': self.activity_page.id,
            'start_date': '2012-02-08',
            'start_time': 50,
            
            'end_date': '2012-02-08',
            'end_time': 100,
            
            'title': 'title',
            'where': 'where',
            'description': 'this is the description'
            }
        response = self.client.post(reverse('post_event'), data)
        last_event_post = Post.objects.all().order_by('-post_time')[0].event_post
        self.assertEqual(last_event_post.description, data['description'])
        self.assertRedirects(response, reverse('activity_page', args=[self.activity_page.url_code]))
        
 
 
