__author__ = 'rui'

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

# get from SO: http://stackoverflow.com/questions/2809547/creating-email-templates-with-django

def send_registration_confirmation(user):
    SUBJECT = 'Welcome to ' + settings.SITE_NAME
    FROM_EMAIL = 'no-reply@activeiu.com'
    TO = user.email

    p = user.get_profile()
    plaintext = get_template('emails/registration/confirmation_email.txt')
    htmly = get_template('emails/registration/confirmation_email.html')

    data = Context({
        'confirmation_code':p.confirmation_code,
        'username':user.username
    })

    text_content = plaintext.render(data)
    html_content = htmly.render(data)

    message = EmailMultiAlternatives(SUBJECT, text_content, FROM_EMAIL, [TO])
    message.attach_alternative(html_content, "text/html")
    message.send()


def send_message_to_post(from_user, content, to_user, action = 'email', page_link = None):

    SUBJECT = 'You got a message from ' + settings.SITE_NAME
    FROM_EMAIL = from_user.email
    TO = to_user.email
    
    if action == 'email':
        plaintext = get_template('emails/send_email_to_post/message_for_email.txt')
        htmly = get_template('emails/send_email_to_post/message_for_email.html')
    else:
        plaintext = get_template('emails/send_comment_message_to_post/message_for_comment.txt')
        htmly = get_template('emails/send_comment_message_to_post/message_for_comment.html')
        
        
        
    data = Context({
        'sender_username':from_user.username,
        'receiver_username':to_user.username,
        'content':content, 
        'site_name': 'ActiveIU',
        'page_url': 'http://www.activeiu.com' + page_link
    })

    text_content = plaintext.render(data)
    html_content = htmly.render(data)

    message = EmailMultiAlternatives(SUBJECT, text_content, FROM_EMAIL, [TO])
    message.attach_alternative(html_content, "text/html")
    message.send()
    
    
    
