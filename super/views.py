from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import Group
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.defaultfilters import slugify
from account.decorators import allowed_users
from account.models import Deposite, User, Currency, TradingPlan, MiningPlan, CopiedTrade, TakeTrade, Withdrawal
from .models import Role, Trader, Coin, NewCoin, Crypto, Forex, StockList
from .models import Currency as Cur
from .forms import CreateTraderForm, CurrencyForm
from .coinlist import coins
from .newcoinlist import coins as ncl
import qrcode
from datetime import datetime
import pytz
import requests

# Create your views here.

# @login_required(login_url='login')
# @allowed_users(allowed_roles=['super'])
def createAdmin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        
        if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
            messages.error(request, 'Email or username already used')
            return redirect('admin-super-admin')

        user = User.objects.create_user(username,email,password)
        user.is_staff = True
        user.is_superuser = True
        user.last_name = last_name
        user.first_name = first_name
        user.role = 'admin'
        user.save()
        
        if not Group.objects.filter(name='super').exists():
            Group.objects.create(name='super')

        User.objects.filter(username = username).update(image = 'passport.jpg')
            
        userid = User.objects.get(username=username).id
        getgroup = Group.objects.get(name='super')
        getgroup.user_set.add(userid)

        messages.success(request, 'Creation successful')
        return redirect('admin-super-admin')
    context = {}
    return render(request, 'super/signup.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def home(request):
    numUsers = len(User.objects.filter(role='client'))
    numTraders = len(Trader.objects.all())
    payment = Deposite.objects.filter(status=2).aggregate(Sum('amount'))
    withdrawal = len(Withdrawal.objects.all())
    deposite = Deposite.objects.all()
    for i in deposite.values():
        current_datetime = datetime.now()
        date_datetime = i.get('expire_time')

        date_datetime = date_datetime.replace(tzinfo=pytz.utc)
        current_datetime = current_datetime.replace(tzinfo=pytz.utc)
        if current_datetime >= date_datetime and i.get('status') != 2:
            Deposite.objects.filter(id=i.get('id')).update(status=3)
    context = {
        'client':numUsers,
        'trader':numTraders,
        'payment':payment,
        'deposite':deposite,
        'withdrawal':withdrawal,
    }
    return render(request, 'super/index.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def user(request):
    users = User.objects.filter(is_active=True)
    context = {
        'users':users,
    }
    return render(request, 'super/userslist.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def updateUser(request, ref):
    act_user = User.objects.get(username=ref)
    traders = CopiedTrade.objects.filter(user=act_user)
    coin = NewCoin.objects.all()
    lenTrade = len(traders)
    takeTrade = TakeTrade.objects.filter(user=act_user)
    if 'updatebalance' in request.POST:
        balance = request.POST.get('balance')
        deposite = request.POST.get('deposite')
        User.objects.filter(username=ref).update(user_balance=balance,user_deposite=deposite)
        messages.success(request, 'Updated')
        return redirect('admin-user-update',ref)
    elif 'email' in request.POST:
        token = request.POST.get('token')
        User.objects.filter(username=ref).update(token=token)
        # Send mail to user
        subject = 'InferraAI UPADTE'
        recipient = [act_user.email]
        text_content = f'Dear {act_user.last_name} your email request token is {token}'
        html_content = f'<div><h3 style="color:purple">InferraAI User Update</h3></div><div><p>Dear {act_user.last_name} your email request token is {token}</div>'
        message = EmailMultiAlternatives(subject=subject, body=text_content, to=recipient)
        message.attach_alternative(html_content, 'text/html')
        message.send()
        messages.success(request, 'Token sent')
        return redirect('admin-user-update',ref)
    elif 'withdraw' in request.POST:
        token = request.POST.get('token')
        User.objects.filter(username=ref).update(withdrawal_token=token)
        # Send mail to user
        subject = 'InferraAI UPADTE'
        recipient = [act_user.email]
        text_content = f'Dear {act_user.last_name} your withdrawal request token is {token}'
        html_content = f'<div><h3 style="color:purple">InferraAI</h3></div><div><p>Dear {act_user.last_name} your withdrawal request token is {token}</div>'
        message = EmailMultiAlternatives(subject=subject, body=text_content, to=recipient)
        message.attach_alternative(html_content, 'text/html')
        message.send()
        messages.success(request, 'Token sent')
        return redirect('admin-user-update',ref)
    elif 'buy' in request.POST:
        get_crypto = request.POST.get('crypto')
        prifit = request.POST.get('profit')
        time = request.POST.get('time')
        amount = request.POST.get('amount')
        trader = request.POST.get('trader')
        
        getTrader = Trader.objects.get(name=trader)
        
        TakeTrade.objects.create(user=act_user, trader=getTrader, crypto=NewCoin.objects.get(name=get_crypto),profit=prifit, time=time, amount=amount)
        messages.success(request, 'Done')
        return redirect('admin-user-update',ref)
    elif 'sell' in request.POST:
        get_crypto = request.POST.get('crypto')
        prifit = request.POST.get('profit')
        time = request.POST.get('time')
        amount = request.POST.get('amount')
        trader = request.POST.get('trader')
        
        getTrader = Trader.objects.get(name=trader)
        
        TakeTrade.objects.create(user=act_user, trader=getTrader, mode='sell', crypto=NewCoin.objects.get(name=get_crypto),profit=prifit, time=time, amount=amount)
        messages.success(request, 'Done')
        return redirect('admin-user-update',ref)
    elif 'verify-identity' in request.POST:
        User.objects.filter(username=ref).update(verify_identity=True)
        messages.success(request, 'Updated')
        return redirect('admin-user-update',ref)
    elif 'verify-address' in request.POST:
        User.objects.filter(username=ref).update(verify_address=True)
        messages.success(request, 'Updated')
        return redirect('admin-user-update',ref)
    elif 'refresh' in request.POST:
        # Update taketrade
        allTrade = TakeTrade.objects.filter(user=act_user)
        for i in allTrade.values():
            current_datetime = datetime.now()
            date_datetime = i.get('expire_time')

            date_datetime = date_datetime.replace(tzinfo=pytz.utc)
            current_datetime = current_datetime.replace(tzinfo=pytz.utc)
            print(current_datetime, date_datetime)
            if current_datetime >= date_datetime and i.get('open_trade'):
                TakeTrade.objects.filter(id=i.get('id')).update(open_trade=False)
                balance = float(act_user.user_balance)
                print(balance, i.get('profit'))
                User.objects.filter(username=act_user.username).update(user_balance = float(i.get('profit')) + balance)
            else:
                continue
        
        # Update payment list
        deposite = Deposite.objects.filter(user=act_user)
        for i in deposite.values():
            current_datetime = datetime.now()
            date_datetime = i.get('expire_time')

            date_datetime = date_datetime.replace(tzinfo=pytz.utc)
            current_datetime = current_datetime.replace(tzinfo=pytz.utc)
            if current_datetime >= date_datetime and i.get('status') != 2:
                Deposite.objects.filter(id=i.get('id')).update(status=3)
        
        messages.success(request, 'Done')
        return redirect('admin-user-update',ref)
        
    elif 'message' in request.POST:
        msg = request.POST.get('message')
        
        # Prepare email
        subject = 'InferraAI UPDATE'
        recipient = [act_user.email]
        
        # Plain text version
        text_content = f'Dear {act_user.last_name}, {msg}'
        
        # HTML version
        html_content = (
            f'<div>'
            f'<h3 style="color:purple">InferraAI</h3>'
            f'<div><p>Dear {act_user.last_name}, <br>{msg}</p></div>'
            f'</div>'
        )
        
        # Send email
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=recipient
        )
        message.attach_alternative(html_content, 'text/html')
        message.send()
        
        # Feedback to admin
        messages.success(request, 'Message sent')
        return redirect('admin-user-update', ref)

        
    context = {
        'client':act_user,
        'trader':traders,
        'len':lenTrade,
        'crypto':coin,
        'taketrade':takeTrade,
    }
    return render(request, 'super/userinfo.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def removeTrade(request, ref):
    getUser = TakeTrade.objects.get(ref=ref)
    if request.method == 'POST':
        TakeTrade.objects.filter(ref=ref).delete()
        messages.success(request, 'Done')
        return redirect('admin-user-update',getUser.user.username)
    context = {'link':getUser}
    return render(request, 'super/removetrade.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def banUser(request, ref):
    if request.method == 'POST':
        User.objects.filter(username=ref).update(is_active=False, ban=True)
        messages.success(request, 'Done')
        return redirect('admin-user-list')
    context = {}
    return render(request, 'super/banuser.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def createTrader(request):
    form = CreateTraderForm()
    if request.method == 'POST':
        form = CreateTraderForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            if Trader.objects.filter(name=name).exists():
                messages.warning(request, 'Trader name already exist')
                return redirect('admin-create-trader')
            form.save()
            messages.success(request, 'Successfully created')
            return redirect('admin-create-trader')
    context = {'form': form}
    return render(request, 'super/createtraders.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def updateTrader(request, ref):
    trader = Trader.objects.get(ref=ref)
    form = CreateTraderForm(instance=trader)
    if request.method == 'POST':
        form = CreateTraderForm(request.POST, request.FILES, instance=trader)
        if form.is_valid():
            name = form.cleaned_data['name']
            if Trader.objects.filter(name=name).exists():
                messages.warning(request, 'Trader name already exist')
                return redirect('admin-update-trader',trader.ref)
            form.save()
            messages.success(request, 'Successfully updated')
            return redirect('admin-update-trader',trader.ref)
    context = {'form': form}
    return render(request, 'super/createtraders.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def deleteTrader(request, ref):
    trader = Trader.objects.filter(ref=ref)
    if request.method == 'POST':
        trader.delete()
        messages.success(request, 'Successfully deleted')
        return redirect('admin-create-trader')
    context = {}
    return render(request, 'super/deletetrader.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def trader(request):
    traders = Trader.objects.all()
    context = {'traders':traders}
    return render(request, 'super/traders.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def adminCancelTrade(request,ref):
    getUser = CopiedTrade.objects.get(ref=ref)
    CopiedTrade.objects.filter(ref=ref).delete()
    return redirect('admin-user-update',getUser.user.username)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def paymentMethod(request):
    currency = Currency.objects.all()
    form = CurrencyForm()
    if request.method == 'POST':
        form = CurrencyForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data.get('address')
            img = qrcode.make(address)
            img_name = address + '.png'
            img.save(settings.MEDIA_ROOT + '/qrcode/' + img_name)
            payment = form.save(commit=False)
            payment.qrcode = 'qrcode/'+img_name
            payment.save()
            messages.success(request, 'payment added')
            return redirect('admin-payment-method')
    context = {'form': form,'currency':currency}
    return render(request, 'super/listpaymentmethod.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def updatePaymentMethod(request,ref):
    currency = Currency.objects.get(ref=ref)
    form = CurrencyForm(instance=currency)
    if request.method == 'POST':
        form = CurrencyForm(request.POST, instance=currency)
        if form.is_valid():
            address = form.cleaned_data.get('address')
            img = qrcode.make(address)
            img_name = address + '.png'
            img.save(settings.MEDIA_ROOT + '/qrcode/' + img_name)
            payment = form.save(commit=False)
            payment.qrcode = 'qrcode/'+img_name
            payment.save()
            messages.success(request, 'payment updated')
            return redirect('admin-update-payment-method',currency.ref)
    context = {'form': form}
    return render(request, 'super/editpaymentmethod.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def deletePaymentMethod(request, ref):
    if request.method == 'POST':
        currency = Currency.objects.filter(ref=ref)
        currency.delete()
        messages.success(request, 'paymeny method deleted')
        return redirect('admin-payment-method')
    return render(request, 'super/deletepaymentmethod.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def payment(request):
    payment = Deposite.objects.all()
    context = {'payment':payment}
    return render(request, 'super/payments.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def paymentApprove(request, ref):
    Deposite.objects.filter(ref=ref).update(status=2)
    # act_user = Deposite.objects.get(ref=ref).user
    # # Send mail to user
    # subject = 'InferraAI UPADTE'
    # recipient = [act_user.email]
    # text_content = f'Dear {act_user.last_name}, Your payment has been approved'
    # html_content = f'<div><h3 style="color:purple">InferraAI</h3></div><div><p>Dear {act_user.last_name}, <br>Your payment has been approved</div>'
    # message = EmailMultiAlternatives(subject=subject, body=text_content, to=recipient)
    # message.attach_alternative(html_content, 'text/html')
    # message.send()
    # messages.success(request, 'Message sent')
    return redirect('admin-payment')
    
@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def withdrawal(request):
    payment = Withdrawal.objects.all()
    context = {'payment':payment}
    return render(request, 'super/withdrawal.html', context)
    
@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def withdrawalApprove(request, ref):
    Withdrawal.objects.filter(ref=ref).update(status=2)
    return redirect('admin-withdrawal')
    
@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def withdrawalDeclined(request, ref):
    Withdrawal.objects.filter(ref=ref).update(status=3)
    return redirect('admin-withdrawal')
        
@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def plan(request):
    context = {}
    return render(request, 'super/plan.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def tradingPlan(request, ref):
    plan = TradingPlan.objects.get(ref=ref)
    if request.method == 'POST':
        package = request.POST.get('package')
        min_amount = request.POST.get('min')
        max_amount = request.POST.get('max')
        TradingPlan.objects.filter(ref=ref).update(name=package, min_amount=min_amount, max_amount=max_amount)
        messages.success(request, 'plan updated')
        return redirect('admin-trading-plan', plan.ref)
    context = {'plan':plan}
    return render(request, 'super/edittradingplan.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def listTradingPlan(request):
    plan = TradingPlan.objects.all()
    context = {'plan':plan}
    return render(request, 'super/listtradingplan.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def miningPlan(request,ref):
    plan = MiningPlan.objects.get(ref=ref)
    if request.method == 'POST':
        package = request.POST.get('package')
        min_amount = request.POST.get('min')
        max_amount = request.POST.get('max')
        MiningPlan.objects.filter(ref=ref).update(name=package, min_amount=min_amount, max_amount=max_amount)
        messages.success(request, 'plan updated')
        return redirect('admin-mining-plan', plan.ref)
    context = {'plan':plan}
    return render(request, 'super/editminingplan.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def listMiningPlan(request):
    plan = MiningPlan.objects.all()
    context = {'plan':plan}
    return render(request, 'super/listminingplan.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def addCoin(request):
    if request.method == 'POST':
        counter = 1
        total = len(coins)
        for i in coins:
            name = i.get('name')
            code = i.get('id')
            if Coin.objects.filter(name=name, code=code).exists():
                counter += 1
                continue
            else:
                Coin.objects.create(name=name, code=code)
                print(f'{counter} of {total} coins added, remaining {total - counter}')
                counter += 1
                
        messages.success(request, 'All added')
        return redirect('admin-home')
    context = {}
    return render(request, 'super/addcoin.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def addCoinPic(request):
    if request.method == 'POST':
        counter = 1
        total = len(ncl)
        for i in ncl:
            name = i.get('name')
            code = i.get('id')
            symbol = i.get('symbol')
            image = i.get('image')
            if NewCoin.objects.filter(name=name, code=code, symbol=symbol).exists():
                counter += 1
                continue
            else:
                NewCoin.objects.create(name=name, code=code, symbol=symbol, image=image)
                print(f'{counter} of {total} coins added, remaining {total - counter}')
                counter += 1
                
        messages.success(request, 'All added')
        return redirect('admin-home')
    context = {}
    return render(request, 'super/addcoinpic.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def addCrypto(request):
    if request.method == 'POST':
        coin_type = request.POST.get('coin')  # 'crypto', 'forex', or 'stock'
        quantity = int(request.POST.get('quantity', 0))

        # Determine URL
        if coin_type == 'stock':
            url = f'https://fcsapi.com/api-v3/stock/list?country=United-states&access_key=097DIrXCOPO0fkm8o7URMBrs8a3AvRK'
        elif coin_type in ['crypto', 'forex']:
            url = f'https://fcsapi.com/api-v3/{coin_type}/list?type={coin_type}&access_key=097DIrXCOPO0fkm8o7URMBrs8a3AvRK'
        else:
            messages.error(request, 'Invalid coin type')
            return redirect('admin-set-coin')

        # Fetch and parse data
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            extract_data = data.get('response', [])
        except Exception as e:
            messages.error(request, f"API Error: {str(e)}")
            return redirect('admin-set-coin')

        # Add coins
        counter = 0
        for item in extract_data:
            name = item.get('name')
            if Cur.objects.filter(name=name, type=coin_type).exists():
                continue

            if counter >= quantity:
                break

            if coin_type == 'stock':
                Cur.objects.create(
                    code=item.get('short_name', ''),
                    symbol=item.get('ccy', ''),
                    name=name,
                    decimal=15,
                    type=coin_type
                )
            else:
                Cur.objects.create(
                    code=item.get('id', ''),
                    symbol=item.get('symbol', ''),
                    name=name,
                    decimal=item.get('decimal', 15),
                    type=coin_type
                )
            counter += 1
            print(f'Added {counter} of {len(extract_data)}')

        messages.success(request, 'Done')
        return redirect('admin-set-coin')

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def addCryptoPic(request):
    if request.method == 'POST':
        coin = request.POST.get('coin')
        quantity = request.POST.get('quantity')
        if coin == 'crypto':
            currency = Cur.objects.filter(type='crypto')
            counter = 0
            total = len(currency)
            for i in currency.values():
                print(i)
                print('----------------------------------------------------')
                url = f"https://fcsapi.com/api-v3/crypto/profile?symbol={i.get('symbol')}&access_key=097DIrXCOPO0fkm8o7URMBrs8a3AvRK"
                r = requests.get(url = url)
                data = r.json()
                extract_data = data.get('response')
                print(extract_data)
                print('+++++++++++++++++++++++++++++++')
                if len(extract_data) < 2:
                    continue
                extract = extract_data[1]
                print(extract)
                print('====================================================')
                if NewCoin.objects.filter(name=extract.get('name'), type=coin).exists():
                    counter += 1
                    print(f'Added {counter} of {total}')
                    continue
                else:
                    if counter >= int(quantity):
                        break
                    NewCoin.objects.create(name=extract.get('name'),code=extract.get('slug'),symbol=extract.get('symbol'),image=extract.get('icon'), type=coin)
                    counter += 1
                    print(f'Added {counter} of {total}')
            messages.success(request, 'Done')
            return redirect('admin-set-coin')
        if coin == 'forex':
            currency = Cur.objects.filter(type='forex')
            counter = 0
            total = len(currency)
            print(total)
            for i in currency.values():
                url = f"https://fcsapi.com/api-v3/forex/profile?id={i.get('code')}&access_key=097DIrXCOPO0fkm8o7URMBrs8a3AvRK"
                r = requests.get(url = url)
                data = r.json()
                extract_data = data.get('response')
                for j in extract_data:
                    if NewCoin.objects.filter(name=j.get('name'), type=coin).exists():
                        counter += 1
                        print(f'Added {counter} of {total}')
                        continue
                    else:
                        if counter >= int(quantity):
                            break
                        NewCoin.objects.create(
                            name=j.get('name'),symbol=j.get('symbol'),image=j.get('icon'), type=coin,
                            code=slugify(j.get('name'))
                        )
                        counter += 1
                        print(f'Added {counter} of {total}')
            messages.success(request, 'Done')
            return redirect('admin-set-coin')
        
        if coin == 'stock':
            currency = Cur.objects.filter(type='stock')
            counter = 0
            total = len(currency)
            for extract in currency.values():
                print(extract)
                if NewCoin.objects.filter(name=extract.get('name'), type=coin).exists():
                    counter += 1
                    print(f'Added {counter} of {total}')
                    continue
                else:
                    if counter >= int(quantity):
                        break
                    NewCoin.objects.create(name=extract.get('name'),code=extract.get('code'),symbol=extract.get('symbol'),image='noimage', type=coin)
                    counter += 1
                    print(f'Added {counter} of {total}')
            messages.success(request, 'Done')
            return redirect('admin-set-coin')

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def setCoin(request):
    api_key = '097DIrXCOPO0fkm8o7URMBrs8a3AvRK'
    apidata = {'crypto': 0, 'forex': 0, 'stock': 0}
    availabledata = {'crypto': 0, 'forex': 0, 'stock': 0}
    gotten = {'crypto': 0, 'forex': 0, 'stock': 0}

    coins, crypto, forex = {}, {}, {}

    # --- Fetch from API and database ---
    for coin_type in ['crypto', 'forex', 'stock']:
        if coin_type == 'stock':
            url = f'https://fcsapi.com/api-v3/stock/list?country=United-states,Japan&access_key={api_key}'
        else:
            url = f'https://fcsapi.com/api-v3/forex/list?type={coin_type}&access_key={api_key}'

        response = requests.get(url).json()
        extract_data = response.get('response', [])
        apidata[coin_type] = len(extract_data)
        gotten[coin_type] = Cur.objects.filter(type=coin_type).count()
        availabledata[coin_type] = NewCoin.objects.filter(type=coin_type).count()

    # --- Search functionality ---
    if 'stock' in request.POST:
        istock = request.POST.get('mstock')
        coins = Cur.objects.filter(name__icontains=istock, type='stock')

    elif 'crypto' in request.POST:
        istock = request.POST.get('mmstock')
        crypto = Cur.objects.filter(name__icontains=istock, type='crypto')

    elif 'forex' in request.POST:
        istock = request.POST.get('mmmstock')
        forex = Cur.objects.filter(name__icontains=istock, type='forex')

    # --- Country-based stock fetching ---
    if 'country' in request.POST:
        country = request.POST.get('mcountry').capitalize()
        url = f'https://fcsapi.com/api-v3/stock/list?country={country}&access_key={api_key}'
        response = requests.get(url).json()
        extract_data = response.get('response')

        if not extract_data:
            messages.warning(request, 'No data found')
            return redirect('admin-set-coin')

        total = len(extract_data)
        counter = 0
        for item in extract_data:
            if not Cur.objects.filter(name=item['name'], type='stock').exists():
                Cur.objects.create(
                    code=item['short_name'],
                    symbol=item['ccy'],
                    name=item['name'],
                    decimal=15,
                    type='stock'
                )
            counter += 1
            print(f'Added {counter} of {total}')

        messages.success(request, 'Done')
        return redirect('admin-set-coin')

    # --- Final context ---
    context = {
        'gotten_crypto': gotten['crypto'],
        'gotten_forex': gotten['forex'],
        'gotten_stock': gotten['stock'],
        'apicrypto': apidata['crypto'],
        'apiforex': apidata['forex'],
        'apistock': apidata['stock'],
        'availablecrypto': availabledata['crypto'],
        'availableforex': availabledata['forex'],
        'availablestock': availabledata['stock'],
        'coin': coins,
        'crypto': crypto,
        'forex': forex,
    }
    return render(request, 'super/addcrypto.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def setCoinAdd(request, ref):
    currency = Cur.objects.get(id=ref)
    if NewCoin.objects.filter(name=currency.name, type='stock').exists():
        messages.warning(request, 'Already exist')
        return redirect('admin-set-coin')
    else:
        NewCoin.objects.create(name=currency.name,code=currency.code,symbol=currency.symbol,image='noimage', type='stock')
        messages.success(request, 'Done')
        return redirect('admin-set-coin')
    
@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def setCryptoAdd(request, ref):
    currency = Cur.objects.get(id=ref)
    if NewCoin.objects.filter(name=currency.name, type='crypto').exists():
        messages.warning(request, 'Already exist')
        return redirect('admin-set-coin')
    else:
        url = f"https://fcsapi.com/api-v3/crypto/profile?symbol={currency.symbol}&access_key=097DIrXCOPO0fkm8o7URMBrs8a3AvRK"
        r = requests.get(url = url)
        data = r.json()
        extract_data = data.get('response')
        if len(extract_data) < 2:
            messages.warning(request, 'Not recognized as crypto')
            return redirect('admin-set-coin')
        extract = extract_data[1]
        NewCoin.objects.create(name=extract.get('name'),code=extract.get('slug'),symbol=extract.get('symbol'),image=extract.get('icon'), type='crypto')
        messages.success(request, 'Done')
        return redirect('admin-set-coin')
    
@login_required(login_url='login')
@allowed_users(allowed_roles=['super'])
def setForexAdd(request, ref):
    currency = Cur.objects.get(id=ref)
    if NewCoin.objects.filter(name=currency.name, type='forex').exists():
        messages.warning(request, 'Already exist')
        return redirect('admin-set-coin')
    else:
        url = f"https://fcsapi.com/api-v3/forex/profile?id={currency.code}&access_key=097DIrXCOPO0fkm8o7URMBrs8a3AvRK"
        r = requests.get(url = url)
        data = r.json()
        extract_data = data.get('response')
        for j in extract_data:
            if NewCoin.objects.filter(name=j.get('name'), type='forex').exists():
                continue
            else:
                NewCoin.objects.create(
                    name=j.get('name'),symbol=j.get('symbol'),image=j.get('icon'), type='forex',
                    code=slugify(j.get('name'))
                )
        messages.success(request, 'Done')
        return redirect('admin-set-coin')