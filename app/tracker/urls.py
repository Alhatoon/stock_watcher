from django.urls import path
from .views import  Tracking, Users


urlpatterns = [
    path('login/', Users.user_login, name='login'),
    path('registration/', Users.registration, name='registration'),
    path('start_tracking/', Tracking.start_tracking, name='start_tracking'),
    path('track_by_id/<uuid:track_id>/', Tracking.track_by_id, name='track_by_id'),
    path('stop_tracking_by_id/<uuid:track_id>/', Tracking.stop_tracking_by_id, name='stop_tracking_by_id'),
    path('track_by_email/<str:email>/', Tracking.track_by_email, name='track_by_email'),
    path('stop_tracking/', Tracking.stop_tracking, name='stop_tracking'),
    path('stop_tracking_confirm/', Tracking.stop_tracking_confirm, name='stop_tracking_confirm'),
    path('opt_out_all/', Tracking.opt_out_all, name='opt_out_all'),
    
]