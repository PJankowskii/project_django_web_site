from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading


# Create your views here.
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid.'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'This email has been used.'}, status=409)
        return JsonResponse({'email_valid': True})


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters.'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'This username already exist, choose another one.'}, status=409)
        return JsonResponse({'username_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        # get user data
        # validate
        # create a user account
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        context = \
            {
                'fieldValues': request.POST
            }
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, "Password is too short")
                    return render(request, 'authentication/register.html', context)
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
                active_url = 'http://' + domain + link
                email_subject = 'Active your account'
                email_body = 'Hello ' + user.username + ', please use this link to verify your account.\n' + active_url
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'noreply@budget.com',
                    [email],
                )
                EmailThread(email).start()
                messages.success(request, "Account successfully created")
                return render(request, 'authentication/register.html')
        return render(request, 'authentication/register.html')


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if not token_generator.check_token(user, token):
                return redirect('login' + '?message=' + 'User already activated')
            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass
        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome ' + user.username + ', you are now logged in')
                    return redirect('expenses')
                messages.error(request, 'Account is not activated, please check your email for activation link')
                return render(request, 'authentication/login.html')
            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/login.html')
        messages.error(request, 'Please fill all fields')
        return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')


class ResetPassword(View):
    def get(self, request):
        return render(request, 'authentication/reset_password.html')

    def post(self, request):
        email = request.POST['email']
        context = \
            {
                'values': request.POST,
            }
        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return render(request, 'authentication/reset_password.html', context)

        current_site = get_current_site(request)
        user = User.objects.filter(email=email)
        if user.exists():
            email_contents = \
                {
                    'user': user[0],
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                    'token': PasswordResetTokenGenerator().make_token(user[0]),
                }

            link = reverse('reset-user-password',
                           kwargs={'uidb64': email_contents['uid'], 'token': email_contents['token']})
            domain = get_current_site(request).domain
            reset_url = 'http://' + domain + link

            email_subject = 'Password reset instructions.'
            email_body = 'Hello, please use this link to reset your password.\n' + reset_url
            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@budget.com',
                [email],
            )
            EmailThread(email).start()

        messages.success(request, 'We sent you a link to reset password')
        return render(request, 'authentication/reset_password.html')


class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = \
            {
                'uidb64': uidb64,
                'token': token,
            }
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password link is invalid, please generate new')
                return render(request, 'authentication/reset_password.html')
        except Exception as identifier:
            pass

        return render(request, 'authentication/set_new_password.html', context)

    def post(self, request, uidb64, token):
        context = \
            {
                'uidb64': uidb64,
                'token': token,
            }
        password = request.POST['password']
        password2 = request.POST['password2']
        if password != password2:
            messages.error(request, "Passwords don't match")
            return render(request, 'authentication/set_new_password.html', context)

        if len(password) < 6:
            messages.error(request, "Password is too short")
            return render(request, 'authentication/set_new_password.html', context)

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect('login')
        except Exception as identifier:
            messages.info(request, 'Something went wrong, try again')
            return render(request, 'authentication/set_new_password.html', context)
