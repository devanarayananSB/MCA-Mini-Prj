from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from accounts.permissions import AdminRequiredMixin, HRRequiredMixin, ApplicantRequiredMixin

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard/admin.html'

class HRDashboardView(HRRequiredMixin, TemplateView):
    template_name = 'dashboard/hr.html'

class ApplicantDashboardView(ApplicantRequiredMixin, TemplateView):
    template_name = 'dashboard/applicant.html'

@login_required
def dashboard_index(request):
    if request.user.is_admin or request.user.is_superuser:
        return redirect('dashboard:admin_dashboard')
    elif request.user.is_hr:
        return redirect('dashboard:hr_dashboard')
    else:
        return redirect('dashboard:applicant_dashboard')
