# views.py
import json
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import TrackingRecord, CustomUser, Token
from .serializers import TrackingRecordSerializer
import random
from django.conf import settings
import string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
# from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from .permissions import IsOwnerOrReadOnly, TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
import secrets
import logging
from django.contrib.auth import login
import uuid
from cassandra.cqlengine.query import DoesNotExist
from django.utils.decorators import method_decorator
from tracker.tasks import check_all_stock_availability


logger = logging.getLogger(__name__)


class Users:
    @csrf_exempt
    def registration(request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            email = data.get('email')
            password = data.get('password')
            
            existing_user = CustomUser.objects.filter(email=email).first()
            if existing_user:
                return JsonResponse({'error': 'A user with this email already exists'}, status=400)

            user = CustomUser()
            user.email = email
            user.set_password(password)
            user.save()
            try:
                # Try to get the token
                token = Token.objects.get(user_email=email)
                # If the token exists, update it
                token.token = uuid.uuid4().hex
                token.save()
            except DoesNotExist:
                # If the token does not exist, create it
                token = Token.create(user_email=email, token=uuid.uuid4().hex)


            return JsonResponse({'token': token.to_dict()}, status=201)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)


    @csrf_exempt
    def user_login(request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            
            email = data.get('email')
            password = data.get('password')
            if email is None or password is None:
                return JsonResponse({'error': 'Missing email or password'}, status=400)
            
            try:
                # Retrieve the user based on the provided email
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'User does not exists'}, status=401)
            
            # Check if the provided password matches the stored password
            if user.check_password(password):
                # Generate a unique token (UUID)
                try:
                    # Try to get the existing token
                    token = Token.objects.get(user_email=email)
                    logger.info(f"Existing token found for user {email}: {token.token}")
                    # Delete the existing token
                    token.delete()
                    logger.info("Existing token deleted.")
                except Token.DoesNotExist:
                    logger.info("No existing token found.")
                
                # Create a new token
                new_token = Token.create(user_email=email, token=uuid.uuid4().hex)
                logger.info(f"New token created: {new_token.token}")
                return JsonResponse({'token': new_token.to_dict()}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
                
        

class Tracking(APIView):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsOwnerOrReadOnly]
    
    @csrf_exempt
    def start_tracking(request):
        if request.method == 'POST':
            user = TokenAuthentication().authenticate(request)
            if user is None:
                raise AuthenticationFailed('Invalid token')
            # Retrieve the JSON data from the request body
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)



            email = data.get('email')
            url = data.get('url')
            stock_check_interval = data.get('stock_check_interval')
            tracked_word = data.get('tracked_word')

            # Validate input parameters
            params = {'email': email, 'url': url, 'stock_check_interval': stock_check_interval, 'tracked_word': tracked_word}

            for param, value in params.items():
                if not value:
                    return JsonResponse({'error': f'Missing {param} parameter'}, status=400)

            try:
                # Let check if product is already being tracked
                existing_product = TrackingRecord.objects.filter(user_email=email, product_url=url).allow_filtering().first()
                if existing_product:
                    return JsonResponse({'error': 'Product already being tracked'}, status=400)

                # Create a new tracked product instance and save to the database
                tracked_product = TrackingRecord.create(
                    user_email=email, 
                    product_url=url, 
                    stock_check_interval=int(stock_check_interval), 
                    tracked_word=tracked_word
                )
                tracked_product.save()
                
                # CRON job to check the stock availability 
                # Create a new periodic task to check the stock availability
                # check_all_stock_availability.delay()
                
                
                return JsonResponse({'message': 'Product tracking started successfully','tracking_record_id': str(tracked_product.id)})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)

    @csrf_exempt
    def stop_tracking_by_id(request, track_id):
        if request.method == 'POST':
            user = TokenAuthentication().authenticate(request)
            if user is None:
                # Authentication failed
                raise AuthenticationFailed('Invalid token')
            try:
                tracked_record = TrackingRecord.objects.get(id=track_id)
                IsOwnerOrReadOnly().has_object_permission(request, tracked_record)
                tracked_record.is_active = False
                tracked_record.save()
                return JsonResponse({'message': 'Tracking stopped successfully'}, status=200)
            except TrackingRecord.DoesNotExist:
                return JsonResponse({'error': 'Tracking record not found'}, status=404)


    def track_by_id(request, track_id):
        if request.method == 'GET':
            user = TokenAuthentication().authenticate(request)
            if user is None:
                # Authentication failed
                raise AuthenticationFailed('Invalid token')
            try:
                tracked_record = TrackingRecord.objects.get(id=track_id)
                IsOwnerOrReadOnly().has_object_permission(request, tracked_record)
                data = {
                    'id': tracked_record.id,
                    'user_email': tracked_record.user_email,
                    'product_url': tracked_record.product_url,
                    'stock_check_interval': tracked_record.stock_check_interval,
                    'tracked_word': tracked_record.tracked_word
                }
                return JsonResponse(data)
            except TrackingRecord.DoesNotExist:
                return JsonResponse({'error': 'Tracking record not found'}, status=404)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)



    def track_by_email(request, email):
        if request.method == 'GET':
            user = TokenAuthentication().authenticate(request)
            if user is None:
                # Authentication failed
                raise AuthenticationFailed('Invalid token')
            try:
                tracked_records = TrackingRecord.objects.filter(user_email=email).allow_filtering()
                data = []
                for tracked_record in tracked_records:
                    IsOwnerOrReadOnly().has_object_permission(request, tracked_record)
                    data.append({
                        'id': tracked_record.id,
                        'product_url': tracked_record.product_url,
                        'stock_check_interval': tracked_record.stock_check_interval,
                        'tracked_word': tracked_record.tracked_word
                    })
                return JsonResponse(data, safe=False)
            except TrackingRecord.DoesNotExist:
                return JsonResponse({'error': 'No tracking records found for this email'}, status=404)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)

    @csrf_exempt
    def stop_tracking(request):
        user = TokenAuthentication().authenticate(request)
        if user is None:
            raise AuthenticationFailed('Invalid token')

        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        email = data.get('email')
        url = data.get('url')
        if not email or not url:
            return JsonResponse({'error': 'Missing email or url'}, status=400)

        otp_token = secrets.token_hex(3)

        try:
            user_profile = CustomUser.objects.get(email=email)
            user_profile.set_otp(otp_token, url)
            user_profile.save()
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        api_host = settings.DEFAULT_FROM_EMAIL
        subject = "OTP for Stop Tracking"
        message = (
            f"Your OTP for stopping tracking for URL {url} is: {otp_token}\n\n"
            f"If you'd like to opt out of tracking this product, click the following link:\n"
            f"{api_host}/stop_tracking_confirm/?email={email}&token={otp_token}\n\n"
            f"If you'd like to opt out of all products, click the following link:\n"
            f"{api_host}/opt_out_all/?email={email}&token={otp_token}"
        )

        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            return JsonResponse({'error': f'Failed to send OTP email: {e}'}, status=500)

        return JsonResponse({'message': 'OTP sent successfully'}, status=200)

    # Single Product Stopping   
    @csrf_exempt
    def stop_tracking_confirm(request):
        email = request.GET.get('email')
        token = request.GET.get('token')

        if not email or not token:
            return JsonResponse({'error': 'Missing email or token'}, status=400)

        try:
            user_profile = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        if not user_profile.check_otp(token):
            return JsonResponse({'error': 'Invalid or expired token'}, status=400)

        url = user_profile.otp_url

        try:
            tracking_record = TrackingRecord.objects.filter(user_email=email, product_url=url).allow_filtering().get()
            tracking_record.is_active = False
            tracking_record.save()
            return JsonResponse({'message': 'Tracking stopped successfully'}, status=200)
        except TrackingRecord.DoesNotExist:
            return JsonResponse({'error': 'Tracking record not found'}, status=404)

    # All Product Stopping
    @csrf_exempt
    def opt_out_all(request):
        email = request.GET.get('email')
        token = request.GET.get('token')

        if not email or not token:
            return JsonResponse({'error': 'Missing email or token'}, status=400)

        try:
            user_profile = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        if not user_profile.check_otp(token):
            return JsonResponse({'error': 'Invalid or expired token'}, status=400)

        tracking_records = TrackingRecord.objects.filter(user_email=email).allow_filtering()
        for tracking_record in tracking_records:
            tracking_record.is_active = False
            tracking_record.save()

        return JsonResponse({'message': 'All active tracking stopped successfully'}, status=200)
