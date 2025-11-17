from django.urls import path
from . import views

urlpatterns = [
    path('', views.case_list, name='case_list'),
    path('<int:pk>/', views.case_detail, name='case_detail'),
    path('new/', views.case_create, name='case_create'),
    path('<int:case_pk>/plan/new/', views.rehabilitation_plan_create, name='rehabilitation_plan_create'),
]