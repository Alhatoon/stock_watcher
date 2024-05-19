from django.urls import path, include

urlpatterns = [

    path('', include('tracker.urls')),  # Include app-level URLs from tracker app
]
