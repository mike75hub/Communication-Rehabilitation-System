from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'clients', views.ClientViewSet, basename='client')
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')
router.register(r'cases', views.CaseViewSet, basename='case')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    # Authentication
    path('auth/login/', views.CustomAuthToken.as_view(), name='api_login'),
    path('auth/user/', views.CurrentUserView.as_view(), name='current_user'),
    
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='api_dashboard'),
    
    # Reports
    path('reports/', views.ReportAPIView.as_view(), name='api_reports'),
    
    # Sync
    path('sync/', views.SyncView.as_view(), name='api_sync'),
    
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional endpoints
    path('officers/', views.OfficerListView.as_view(), name='api_officers'),
    path('judges/', views.JudgeListView.as_view(), name='api_judges'),
]