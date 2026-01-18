from django.shortcuts import render
from .froms import RegistrationForm, LoginForm
from .models import Account
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.http import HttpResponse

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            username = email.split('@')[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            user.phone_number = phone_number
            user.is_active = False   # 🔐 IMPORTANT
            user.save()

            # EMAIL VERIFICATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'

            email_body = render_to_string(
                'accounts/account_verification_email.html',
                {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                }
            )

            send_email = EmailMessage(
                mail_subject,
                email_body,
                to=[email]
            )
            send_email.send()

            messages.success(
                request,
                'Registration successful. Please check your email to activate your account.'
            )

            return redirect('login')

    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')  # replace 'home' with your home page URL name
            else:
                form.add_error(None, 'Invalid email or password')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')

def activate(request, uidb64, token):
    return HttpResponse('ok')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgot_password(request):
    print("FORGOT PASSWORD VIEW HIT")  # 👈 ADD THIS

    if request.method == 'POST':
        print("POST REQUEST RECEIVED")  # 👈 ADD THIS

        email = request.POST.get('email')
        print("EMAIL RECEIVED:", email)  # 👈 ADD THIS

        if Account.objects.filter(email=email).exists():
            print("USER EXISTS")  # 👈 ADD THIS

            user = Account.objects.get(email=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            email_message = EmailMessage(
                mail_subject,
                message,
                to=[email]
            )

            email_message.send()
            print("EMAIL SENT")  # 👈 ADD THIS

            messages.success(request, 'Password reset email has been sent.')
            return redirect('login')

        else:
            print("USER DOES NOT EXIST")  # 👈 ADD THIS
            messages.error(request, 'Account does not exist.')

    return render(request, 'accounts/forgot_password.html')



def reset_password_validate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        request.session['reset_uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has expired.')
        return redirect('forgot_password')


def reset_password(request):
    print("RESET PASSWORD VIEW HIT")
    print("METHOD:", request.method)

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password')

        uid = request.session.get('reset_uid')
        if not uid:
            messages.error(request, 'Unauthorized request.')
            return redirect('forgot_password')

        user = Account.objects.get(pk=uid)
        user.set_password(password)
        user.save()

        del request.session['reset_uid']

        messages.success(request, 'Password reset successful.')
        return redirect('login')

    return render(request, 'accounts/reset_password.html')
