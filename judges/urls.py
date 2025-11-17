from django.urls import path
from . import views

app_name = 'judges'

urlpatterns = [
    path('dashboard/', views.judge_dashboard, name='judge_dashboard'),
    path('cases/', views.judge_cases, name='judge_cases'),
    path('cases/<int:pk>/', views.judge_case_detail, name='judge_case_detail'),
    path('calendar/', views.court_calendar, name='court_calendar'),
    path('reviews/', views.judicial_reviews, name='judicial_reviews'),
    
    # New functionality URLs
    path('update-sentencing/', views.update_sentencing, name='update_sentencing'),
    path('complete-review/', views.complete_review, name='complete_review'),
    path('request-info/', views.request_info, name='request_info'),
    path('reschedule-hearing/', views.reschedule_hearing, name='reschedule_hearing'),
]