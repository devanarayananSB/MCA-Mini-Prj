from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from .models import UserProfile, ActivityLog

User = get_user_model()

def get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Check if profile exists before saving
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            UserProfile.objects.create(user=instance)

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    ActivityLog.objects.create(
        user=user,
        action="Login Success",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details=f"User {user.email} logged in successfully."
    )

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if user:
        ActivityLog.objects.create(
            user=user,
            action="Logout",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details=f"User {user.email} logged out successfully."
        )

@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    email = credentials.get('email', credentials.get('username', 'Unknown'))
    ActivityLog.objects.create(
        user=None,
        action="Login Failed",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
        details=f"Failed login attempt for identifier: {email}"
    )
