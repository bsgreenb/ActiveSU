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


def message_to_post(from_user,  to_user_list, content = None, action = 'email', page_link = None):

    SUBJECT = 'You got a message from ' + settings.SITE_NAME
    FROM_EMAIL = from_user.email
    TO = []
    
    for user in to_user_list:
        TO.append(user.email)
    
    if action == 'email':
        plaintext = get_template('emails/send_email_to_post/message_for_email.txt')
        htmly = get_template('emails/send_email_to_post/message_for_email.html')
    else:
        plaintext = get_template('emails/send_comment_message_to_post/message_for_comment.txt')
        htmly = get_template('emails/send_comment_message_to_post/message_for_comment.html')
        
    page_url = 'http://www.activeiu.com/'
    
    if page_link:
        page_url = page_url + page_link
    
    if action == 'email':
        receiver_username = to_user_list[0].username
    else:
        receiver_username = ''
        
    data = Context({
        'sender_username':from_user.username,
        'receiver_username':receiver_username,
        'content':content, 
        'site_name': 'ActiveSU',
        'page_url': page_url
    })

    text_content = plaintext.render(data)
    html_content = htmly.render(data)

    message = EmailMultiAlternatives(SUBJECT, text_content, FROM_EMAIL, TO)
    message.attach_alternative(html_content, "text/html")
    message.send()
    
    
    
