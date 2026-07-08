from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class AdminRequiredMixin(UserPassesTestMixin):
    """
    Mixin to restrict access only to Administrators.
    """
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_admin or self.request.user.is_superuser)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You do not have administrative privileges to view this page.")
        return super().handle_no_permission()


class HRRequiredMixin(UserPassesTestMixin):
    """
    Mixin to restrict access only to HR managers and Administrators.
    """
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_hr or self.request.user.is_admin or self.request.user.is_superuser
        )

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You do not have HR privileges to view this page.")
        return super().handle_no_permission()


class ApplicantRequiredMixin(UserPassesTestMixin):
    """
    Mixin to restrict access only to Applicants.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_applicant

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("This page is reserved for job applicants.")
        return super().handle_no_permission()
