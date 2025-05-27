from django.shortcuts import redirect, render
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from super.models import Contact
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site

from account.functions import telegram, welcomeEmail
from account.decorators import allowed_users
from account.models import User
from account.tokens import account_activation_token

# Create your views here.

def home(request):
    context = {}
    return render(request, 'fronpage/index.html', context)

def contact(request):
    if request.method == 'POST':
        last = request.POST.get('last')
        first = request.POST.get('first')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        subject = request.POST.get('subject')
        reason = request.POST.get('reason')
        message = request.POST.get('message')
        
        # Send message to admin
        telegram(f'Hello admin, you have a message from {last} {first} (unregistered user).\nSubject: {subject}\nEmail: {email}\nMobile: {mobile}\nReason: {reason}\n\n\n\n{message}')
        messages.success(request, 'sent')
        
    context = {}
    return render(request, 'fronpage/contactus.html', context)

def doge(request):
    context = {}
    return render(request, 'fronpage/dogemining.html', context)

def bitcoin(request):
    context = {}
    return render(request, 'fronpage/bitcoinmining.html', context)

def aboutMining(request):
    context = {}
    return render(request, 'fronpage/aboutmining.html', context)

def responsibleTrading(request):
    context = {}
    return render(request, 'fronpage/responsibletrading.html', context)

def whatIsLeverage(request):
    context = {}
    return render(request, 'fronpage/whatisleverage.html', context)

def copyExpertTrades(request):
    context = {}
    return render(request, 'fronpage/copytrading.html', context)

def optionsTrading(request):
    context = {}
    return render(request, 'fronpage/optionstrading.html', context)

def cryptoTrading(request):
    context = {}
    return render(request, 'fronpage/cryptotrading.html', context)

def stockTrading(request):
    context = {}
    return render(request, 'fronpage/stocktrading.html', context)

def forexTrading(request):
    context = {}
    return render(request, 'fronpage/forextrading.html', context)

def generalRisk(request):
    context = {}
    return render(request, 'fronpage/generalrisk.html', context)

def termOfService(request):
    context = {}
    return render(request, 'fronpage/termsofservice.html', context)

def privacyPolicy(request):
    context = {}
    return render(request, 'fronpage/privacypolicy.html', context)

def cookie(request):
    context = {}
    return render(request, 'fronpage/cookie.html', context)

def about(request):
    context = {}
    return render(request, 'fronpage/aboutus.html', context)

def cryptoMining(request):
    context = {}
    return render(request, 'fronpage/cryptominning.html', context)

def faq(request):
    context = {}
    return render(request, 'fronpage/faq.html', context)

def loginuser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            if user.password_reset:
                return redirect('password_reset',username)
            else:
                if user.role == 'admin':
                    return redirect('admin-home')
                else:
                    return redirect('home')
        else:
            messages.error(request,'Incorrect email or password')
            return redirect('login')
    return render(request, 'fronpage/signin.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def logoutuser(request):
    logout(request)
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        currency = request.POST.get('currency')

        if ' ' in username:
            messages.error(request, 'Invalid email address')
            return redirect('login')

        if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
            messages.error(request, 'Email or username already used')
            return redirect('login')

        if pass1 != pass2:
            messages.error(request, 'Password did not match')
            return redirect('login')

        user = User.objects.create_user(username,email,pass1)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = False
        user.last_name = last_name
        user.first_name = first_name
        user.currency = currency
        user.role = 'client'
        user.psw = pass1
        user.save()

        if not Group.objects.filter(name='client').exists():
            Group.objects.create(name='client')

        User.objects.filter(username = username).update(image = 'passport.jpg')

        userid = User.objects.get(username=username).id
        getgroup = Group.objects.get(name='client')
        getgroup.user_set.add(userid)

        # Send welcome email
        welcomeEmail(request, user, email)

        messages.success(request, 'Registration successful')
        return redirect('login')

    content = {}
    return render(request, 'fronpage/signup.html')

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.verify_email = True
        user.save()
        messages.success(request, 'Verification was successful')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid')
    return redirect('home')
