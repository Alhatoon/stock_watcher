from django.contrib import admin
from django.urls import path, include

from tracker import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracker.urls')),  # Include app-level URLs from tracker app
]
