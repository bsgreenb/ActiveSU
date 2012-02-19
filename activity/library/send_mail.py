__author__ = 'rui'

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

# get from SO: http://stackoverflow.com/questions/2809547/creating-email-templates-with-django

def send_registration_confirmation(user):
    p = user.get_profile()
    plaintext = get_template('emails/registration/confirmation_email.txt')
    htmly = get_template('emails/registration/confirmation_email.html')

    data = Context({
        'confiramtion_code':p.confirmation_code,
        'username':user.username
    })

    subject, from_email, to = ('', '', '')
    text_content = plaintext.render(data)
    html_content = htmly.render(data)

    message = EmailMultiAlternatives(subject, text_content, from_email, [to])
    message.attach_alternative(html_content, "text/html")
    message.send()


def send_email_to_post(post, content, to_user):
    plaintext = get_template('emails/send_email_to_post/message.txt')
    htmly = get_template('emails/send_email_to_post/message.html')

    data = Context({
        'sender_username':post.user.username,
        'receiver_username':to_user.username,
        'content':content
    })

    subject, from_email, to = ('', '', '')
    text_content = plaintext.render(data)
    html_content = htmly.render(data)

    message = EmailMultiAlternatives(subject, text_content, from_email, [to])
    message.attach_alternative(html_content, "text/html")
    message.send()