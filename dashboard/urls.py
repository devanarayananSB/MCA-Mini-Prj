from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('hr/', views.HRDashboardView.as_view(), name='hr_dashboard'),
    path('applicant/', views.ApplicantDashboardView.as_view(), name='applicant_dashboard'),
]
