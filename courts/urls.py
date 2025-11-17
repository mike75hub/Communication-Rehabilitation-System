from django.urls import path
from . import views

app_name = 'courts'

urlpatterns = [
    # Court management
    path('', views.court_dashboard, name='court_dashboard'),
    path('courts/', views.court_list, name='court_list'),
    path('courts/create/', views.court_create, name='court_create'),
    path('courts/<int:pk>/', views.court_detail, name='court_detail'),
    path('courts/<int:pk>/edit/', views.court_edit, name='court_edit'),
    path('courts/<int:pk>/delete/', views.court_delete, name='court_delete'),
    
    # Court cases
    path('cases/', views.court_case_list, name='court_case_list'),
    path('cases/create/', views.court_case_create, name='court_case_create'),
    path('cases/<int:pk>/', views.court_case_detail, name='court_case_detail'),
    path('cases/<int:pk>/edit/', views.court_case_edit, name='court_case_edit'),
    
    # Hearings
    path('hearings/', views.hearing_list, name='hearing_list'),
    path('hearings/create/', views.hearing_create, name='hearing_create'),
    path('hearings/<int:pk>/', views.hearing_detail, name='hearing_detail'),
    path('hearings/<int:pk>/edit/', views.hearing_edit, name='hearing_edit'),
    path('hearings/<int:pk>/update-status/', views.hearing_update_status, name='hearing_update_status'),
    
    # Court orders
    path('orders/', views.court_order_list, name='court_order_list'),
    path('orders/create/', views.court_order_create, name='court_order_create'),
    path('orders/<int:pk>/', views.court_order_detail, name='court_order_detail'),
    path('orders/<int:pk>/edit/', views.court_order_edit, name='court_order_edit'),
    
    # Calendar and overview
    path('calendar/', views.court_calendar_overview, name='court_calendar_overview'),
    
    # AJAX endpoints
    path('ajax/get-judges/', views.get_judges_for_court, name='get_judges_for_court'),
    path('ajax/get-court-cases/', views.get_court_cases_for_judge, name='get_court_cases_for_judge'),
]