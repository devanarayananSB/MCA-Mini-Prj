import logging
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, View
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.signing import Signer, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from .models import UserProfile, ActivityLog
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm

User = get_user_model()
signer = Signer()
logger = logging.getLogger(__name__)

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        # Save user as inactive until verified
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        
        # Log registration activity
        ActivityLog.objects.create(
            user=user,
            action="Registration Initiated",
            ip_address=self.request.META.get('REMOTE_ADDR'),
            details=f"User {user.email} registered. Pending email verification."
        )
        
        # Generate signing token for verification link
        token = signer.sign(user.email)
        
        # Build verification URL
        current_site = get_current_site(self.request)
        verification_url = f"http://{current_site.domain}/accounts/verify-email/{token}/"
        
        # Send confirmation email
        subject = "Verify your RATS Account"
        message = f"Hi {user.first_name},\n\nPlease verify your account by clicking the link below:\n{verification_url}\n\nRegards,\nRATS Team"
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.success(self.request, "Registration successful! Please check your email to verify your account.")
        except Exception as e:
            logger.error(f"Failed to send email verification: {str(e)}")
            messages.warning(self.request, "Registration successful, but we failed to send a verification email. Please contact support.")
            
        return super().form_valid(form)


class VerifyEmailView(View):
    def get(self, request, token):
        try:
            # Token expires in 2 hours (7200 seconds)
            email = signer.unsign(token, max_age=7200)
            user = User.objects.get(email=email)
            
            if not user.is_email_verified:
                user.is_email_verified = True
                user.is_active = True
                user.save()
                
                ActivityLog.objects.create(
                    user=user,
                    action="Email Verified",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    details=f"User {user.email} verified their email successfully."
                )
                
                messages.success(request, "Your email has been successfully verified! You can now log in.")
            else:
                messages.info(request, "Your email is already verified.")
                
        except SignatureExpired:
            messages.error(request, "The verification link has expired.")
        except (BadSignature, User.DoesNotExist):
            messages.error(request, "Invalid verification link.")
            
        return redirect('accounts:login')


class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return reverse_lazy('dashboard:admin_dashboard')
        elif user.is_hr:
            return reverse_lazy('dashboard:hr_dashboard')
        else:
            return reverse_lazy('dashboard:applicant_dashboard')


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect('accounts:login')
        
    def post(self, request):
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect('accounts:login')


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile_edit')
    
    def get_object(self, queryset=None):
        return self.request.user.profile
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_info'] = self.request.user
        else:
            context['user_info'] = self.request.user
        return context
        
    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        
        ActivityLog.objects.create(
            user=user,
            action="Profile Updated",
            ip_address=self.request.META.get('REMOTE_ADDR'),
            details="User updated profile details."
        )
        
        messages.success(self.request, "Your profile has been updated successfully.")
        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def form_valid(self, form):
        messages.success(self.request, "If the email matches an active account, we have sent instructions to reset your password.")
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    
    def form_valid(self, form):
        messages.success(self.request, "Your password has been reset successfully! You can now log in.")
        return super().form_valid(form)
