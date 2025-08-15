from django.shortcuts import render, redirect
from payment.models import ShippingAddress, Order, OrderItem
from .forms import CreateUserForm, LoginForm, UpdateUserForm
from payment.forms import ShippingForm
from django.contrib.sites.shortcuts import get_current_site
from . token import user_tokenizer_generate
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Account Verfication Email'
            message = render_to_string('account/registration/email_verify.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': user_tokenizer_generate.make_token(user),
            })

            user.email_user(subject=subject, message=message)
            return redirect('email_sent')

        
    context = {'form': form}
    return render(request, 'account/registration/register.html', context=context)

def email_verify(request, uidb64, token):
    unique_id = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=unique_id)
    if user and user_tokenizer_generate.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('email_success')
    else:
        return redirect('email_fail')

def email_sent(request):
    return render(request, 'account/registration/email_sent.html')

def email_success(request):
    return render(request, 'account/registration/email_success.html')

def email_fail(request):
    return render(request, 'account/registration/email_fail.html')

def my_login(request):
    form = LoginForm
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('dashboard')  
            
    context = {'form': form}
    return render(request, 'account/my_login.html', context=context)

def user_logout(request):
    try:
        for key in list(request.session.keys()):
            if key == 'session_key':
                continue
            else:
                del request.session[key]
    except KeyError:
        pass
    messages.success(request, 'You have been logged out successfully!')
    return redirect('store')  


@login_required(login_url='my_login')
def dashboard(request):
    context = {'user': request.user}
    return render(request, 'account/dashboard.html', context=context)

@login_required(login_url='my_login')
def profile_management(request):
    form = UpdateUserForm(instance=request.user)  
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.info(request, 'Account is now updated!')
            return redirect('dashboard')  
    else:
        form = UpdateUserForm(instance=request.user)  
    context = {'form': form}
    return render(request, 'account/profile_management.html', context=context)  

@login_required(login_url='my_login')
def delete_account(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        user.delete()  
        messages.error(request, 'Account has now been deleted!')
        return redirect('store')  
    return render(request, 'account/delete_account.html')  

@login_required(login_url='my_login')
def manage_shipping(request):
    try:
        shipping = ShippingAddress.objects.get(user=request.user.id)
    except ShippingAddress.DoesNotExist:
        shipping = None

    form = ShippingForm(instance=shipping)

    if request.method == 'POST':
        form = ShippingForm(request.POST, instance=shipping)
        if form.is_valid():
            shipping_user = form.save(commit=False)
            shipping_user.user = request.user
            shipping_user.save()
            messages.info(request, "Update success!")
            return redirect('dashboard')
    context = {'form':form}
    return render(request, 'account/manage_shipping.html', context=context)

@login_required(login_url='my_login')
def track_orders(request):
    try:
        orders = OrderItem.objects.filter(user=request.user)
        context = {'orders': orders}
        return render(request, 'account/track_orders.html', context=context)  
    except OrderItem.DoesNotExist:
        return render(request, 'account/track_orders.html', context=context)
    return render(request, 'account/track_orders.html')  
