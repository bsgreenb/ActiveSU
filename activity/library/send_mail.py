__author__ = 'rui'

from django.core.mail import send_mail

def send_registration_confirmation(user):
    p = user.get_profile()
    title = "ActiveSU account confirmation"
    content = "http://www.activesu.com/register/success/" + str(p.confirmation_code) + "/" + user.username
    send_mail(title, content, 'no-reply@gsick.com', [user.email], fail_silently=False)


def send_email_to_post(post, content, to_user):
    title = ""
    return send_mail(title, content, post.user.email, [to_user.email])