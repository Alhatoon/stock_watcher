from django.urls import path
from . import views
from .views import UserLogin, UserRegistration


urlpatterns = [
    path('login/', UserLogin.as_view(), name='user_login'),
    path('register/', UserRegistration.as_view(), name='user_registration'),
    path('start_tracking/', views.start_tracking, name='start_tracking'),
    path('track_by_id/<int:track_id>/', views.track_by_id, name='track_by_id'),
    path('track_by_email/<str:email>/', views.track_by_email, name='track_by_email'),
    path('stop_tracking/', views.stop_tracking, name='stop_tracking'), 
    path('stop_tracking_confirm/', views.stop_tracking_confirm, name='stop_tracking_confirm'),
    
]

