from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),  
    path('users/', include('users.urls')),
    path('clients/', include('clients.urls')),
    path('cases/', include('cases.urls')),
    path('appointments/', include('appointments.urls')),
    path('reporting/', include('reporting.urls')),
    path('comms/', include('comms.urls')),
    path('api/', include('api.urls')),
    path('judges/', include('judges.urls')),
    path('courts/', include('courts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)