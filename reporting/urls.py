from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('clients/', views.client_report, name='client_report'),
    path('appointments/', views.appointment_report, name='appointment_report'),
    path('officers/', views.officer_report, name='officer_report'),
    path('clients/pdf/', views.client_report_pdf, name='client_report_pdf'),
]