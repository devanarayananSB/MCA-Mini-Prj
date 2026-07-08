from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import UserProfile, ActivityLog

User = get_user_model()

class AccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testapplicant',
            email='applicant@example.com',
            password='testpassword123',
            role=User.ROLE_APPLICANT
        )
        
    def test_user_creation_and_profile(self):
        """Verify that a user is successfully created with the correct role and a profile is automatically generated."""
        self.assertEqual(self.user.email, 'applicant@example.com')
        self.assertEqual(self.user.role, User.ROLE_APPLICANT)
        self.assertTrue(self.user.is_applicant)
        self.assertFalse(self.user.is_hr)
        self.assertFalse(self.user.is_admin)
        
        # Profile signal check
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)
        
    def test_admin_and_hr_roles(self):
        """Verify Admin and HR roles configuration."""
        admin_user = User.objects.create_user(
            username='testadmin',
            email='admin@example.com',
            password='adminpassword123',
            role=User.ROLE_ADMIN
        )
        hr_user = User.objects.create_user(
            username='testhr',
            email='hr@example.com',
            password='hrpassword123',
            role=User.ROLE_HR
        )
        
        self.assertTrue(admin_user.is_admin)
        self.assertTrue(hr_user.is_hr)

    def test_activity_logging(self):
        """Verify ActivityLog creation."""
        log = ActivityLog.objects.create(
            user=self.user,
            action="Test Action",
            ip_address="127.0.0.1",
            details="Some test details"
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, "Test Action")
        self.assertEqual(log.ip_address, "127.0.0.1")
