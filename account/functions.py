from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.core.mail import send_mail, EmailMultiAlternatives
from .tokens import account_activation_token
import requests

def activateEmail(request, user, to_email):
    mail_subject = 'Account verification'
    message = render_to_string('account/activate.html', {
        'user':user.username,
        'email':to_email,
        'domain':get_current_site(request).domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':account_activation_token.make_token(user),
        'protocol':'https' if request.is_secure else 'http'
    }
    )
    # email = EmailMessage(mail_subject, message, to=[to_email])
    email = EmailMultiAlternatives(mail_subject, message, to=[to_email])
    email.attach_alternative(message, "text/html")
    email.content_subtype = 'html'
    email.send()
    if email.send():
        messages.success(request, f'A verification mail has been sent to {to_email}, pls verify before login')
    else:
        messages.error(request, f'Problem sending email to {to_email}, please try again')

def welcomeEmail(request, user, to_email):
    mail_subject = 'Account verification'
    message = render_to_string('account/welcome.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'protocol': 'https' if request.is_secure() else 'http',
    })

    email = EmailMultiAlternatives(mail_subject, message, to=[to_email])
    email.attach_alternative(message, "text/html")
    email.content_subtype = 'html'

    sent_count = email.send()
    if sent_count > 0:
        messages.success(request, 'Registration successful.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, please try again.')
        
def telegram(message):
    TOKEN = "8006948716:AAHrcypxchK-fwF1qoXkw46pzU9JBWO4iUY"
    chat_id = ['1322959136','6963975811']

    for i in chat_id:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={i}&text={message}"
        requests.get(url)
    
def checkUserName(request,username):
    if ' ' in username:
        messages.error(request, 'Remove space from the username')
        return redirect('register')

    for i in username:
        print(ord(i))
        if ord(i) >= 48 and ord(i) <= 57:
            print('username correct')
        elif ord(i) >= 97 and ord(i) <= 122:
            print('username correct')
        else:
            messages.error(request, 'Invalid username')
            return redirect('register')
    
    return 'ok'

def usd_to_btc(usd_amount):
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    
    btc_price = data['bitcoin']['usd']  # USD per 1 BTC
    btc_amount = usd_amount / btc_price
    return btc_amount