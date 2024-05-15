from django.urls import path
from .views import  Tracking, Users


urlpatterns = [
    path('login/', Users.user_login, name='login'),
    path('registration/', Users.registration, name='registration'),
    path('start_tracking/', Tracking.start_tracking, name='start_tracking'),
    path('track_by_id/<int:track_id>/', Tracking.track_by_id, name='track_by_id'),
    path('track_by_email/<str:email>/', Tracking.track_by_email, name='track_by_email'),
    path('stop_tracking/', Tracking.stop_tracking, name='stop_tracking'), 
    path('stop_tracking_confirm/', Tracking.stop_tracking_confirm, name='stop_tracking_confirm'),
    
]

# urlpatterns = [
#     path('login/', User.as_view(), name='login'),
#     path('register/', User.as_view(), name='registration'),
#     path('start_tracking/', Tracking.as_view({'post': 'start_tracking'}), name='start_tracking'),
#     path('track_by_id/<int:track_id>/', Tracking.as_view({'get': 'track_by_id'}), name='track_by_id'),
#     path('track_by_email/<str:email>/', Tracking.as_view({'get': 'track_by_email'}), name='track_by_email'),
#     path('stop_tracking/', Tracking.as_view({'post': 'stop_tracking'}), name='stop_tracking'), 
#     path('stop_tracking_confirm/', Tracking.as_view({'post': 'stop_tracking_confirm'}), name='stop_tracking_confirm'),
# ]