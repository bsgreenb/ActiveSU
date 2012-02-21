import datetime
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail
from django.test import Client

from activity.models import *
from activity.forms import *

FAKE_EMAIL = 'fakeuser@umail.iu.edu'

def create_and_login_user():

    client = Client()

    password = 'fakeuser'
    
    user = User.objects.create_user('fakeuser', FAKE_EMAIL, password)
    user.is_active = True
    user.save()
    
    login_successful = client.login(username=user.username, password=password)
    
    return user, client

# form #

class Test_RegistrationForm(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.data = {
            'username':'testcase',
            'email':FAKE_EMAIL,
            'password1':'mopyard1',
            'password2':'mopyard1'
        }

    def test_valid_case(self):
        self.assertTrue(RegistrationForm(self.data).is_valid())

    def test_invalid_cases(self):
        user = User.objects.get(pk=1)
        existing_username = user.username
        existing_email = user.email

        cases = {
            # cover clean_password2, clean_username and clean_email casess
            'password2':'mopyard111',
            'username':existing_username,
            'email':existing_email,
            'not_iu_email':'test@cc.edu'
        }

        for case in cases:
            if case == 'password2':
                self.data['password2'] = cases['password2']
            elif case == 'username':
                self.data['username'] = cases['username']
            elif case == 'email':
                self.data['email'] = cases['email']
            elif case == 'not_iu_email':
                self.data['email'] = cases['not_iu_email']

        f = RegistrationForm(self.data)
        self.assertFalse(f.is_valid())

# view #
class Test_Logout_Page(TestCase):
    fixtures = ['test_data.json']

    def test_logout_page(self):
        # requirement 1. a logged in user can be logged out.
        user = User.objects.create_user('fakename', FAKE_EMAIL, 'wangshi')

        login = self.client.login(username = user.username, password='wangshi') # can't use user.password because it's hashed

        self.assertTrue(login) # logged in user.
        response = self.client.get(reverse('logout'), follow=True)
        #todo how I can test out the user is anonymous now.
        self.assertTemplateUsed(response, 'main_page.html')


class Test_Register_Page(TestCase):

    fixtures = ['test_data.json']
    
    def setUp(self):
        self.data = {'username':'test', 'password1':'mopyard1', 'password2':'mopyard2', 'email':FAKE_EMAIL} # it's invalid data. the password is different

    def test_get(self):
        response = self.client.get(reverse('register'))
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_post_invalid_data(self):
        response = self.client.post(reverse('register'), self.data)
        self.assertTemplateUsed(response, 'registration/register.html') # invalid data.

    def test_post_valid_data(self):
        self.data['password2'] = 'mopyard1'  # now, the data is valid
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
        user = self.users[0]
        user.is_active = False
        user.save()
        
        z = User.objects.get(username = user.username)
               
        confirmation_code = user.get_profile().confirmation_code[:-5] + 'kkkpq'
        
        response = self.client.get(reverse('register_success', kwargs={'confirmation_code' : confirmation_code, 'username': user.username}))
                        
        updated_user = User.objects.get(username = user.username)
        
        self.assertFalse(updated_user.is_active)
        
        self.assertTemplateUsed(response, 'registration/register_confirm_success.html')
        self.assertContains(response, 'Sorry')
        
        
    def test_invalid_user(self):
        user = self.users[0]
        response = self.client.get(reverse('register_success', kwargs={'confirmation_code' : user.get_profile().confirmation_code, 'username': 'Iamatestuser'}))
        
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
        response = self.client.get(reverse('unsubscribe_page', kwargs={'username': 'thisisijustatestusername', 'unsubscribe_code':user.get_profile().unsubscribe_code}))
        
        self.assertContains(response, 'match any account', status_code = 200)
        
        
    def test_invalid_unsubscribe(self):
        user = self.users[0]
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
    
    def setUp(self):
        self.created_user, self.client = create_and_login_user()
        self.users = User.objects.all()
        self.activity_page = Activity_Page.objects.all()[0]
        
    def test_create_user_for_activity_page(self):
        response = self.client.post(reverse('activity_page', args=[self.activity_page.url_code]))
        
        self.assertIsNotNone(Activity_Page_User.objects.get(user = self.created_user))
        
    def test_invalid_url(self):
        response = self.client.post(reverse('activity_page', args=['thisisjustatesturl']))
        self.assertRedirects(response, reverse('main_page'))
    
    
    #todo.  come back and see how I can test out the valid post
    
      
class Test_Message_To_Post(TestCase):

    fixtures = ['test_data.json']
    
    def setUp(self):
        self.created_user, self.client = create_and_login_user()
        
    def test_message_to_post(self):
    
        post = Post.objects.filter(activity_page__show_email=True)[0]
        
        post_data = {'post_id': post.id, 'post_message': 'hello, I want to meet for tennis'}
        
        response = self.client.post(reverse('send_message_to_post'), post_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(len(mail.outbox), 1)
        
        self.assertEqual(mail.outbox[0].subject, 'You got a message from ActiveIU')
                
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
        
        
class Test_Submit_Comment(TestCase):

    fixtures = ['test_data.json']


    def setUp(self):
        self.created_user, self.client = create_and_login_user()
        self.post = Post.objects.all()[0]
        
    def test_submit_comment(self):
        data = {
            'post':self.post.id,
            'content': 'this is a comment. zzzzzzz'
            }
        
        response = self.client.post(reverse('post_comment'), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        last_comment = Comment.objects.all().order_by('-comment_time')[0]
        self.assertEqual(last_comment.content, data['content'])
        self.assertEqual(last_comment.post, self.post)
        
        self.assertContains(response, 'OK')
             
             
             
class Test_Submit_Text_Post(TestCase):
    fixtures = ['test_data.json']
    
    def setUp(self):
        self.created_user, self.client = create_and_login_user()
        self.activity_page = Activity_Page.objects.get(pk=1)
        
    def test_submit_text_post(self):
        content = 'hello. I want to play basketball with someone'
        data = {
            'content':content,
            'activity_page': self.activity_page.id
            }
            
        response = self.client.post(reverse('post_message'), data)
        
        last_text_post = Post.objects.all().order_by('-post_time')[0].text_post
        
        self.assertEqual(last_text_post.content, content)
        
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
        
 
 
        
        
        
        

        


