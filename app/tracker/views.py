# views.py
import json
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import TrackingRecord, CustomUser, Token
from .serializers import TrackingRecordSerializer
import random
import string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from .permissions import IsOwnerOrReadOnly, TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

import secrets
import logging
from django.contrib.auth import login
import uuid
from cassandra.cqlengine.query import DoesNotExist


logger = logging.getLogger(__name__)

class Users:
    @csrf_exempt
    def registration(request):
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            existing_user = CustomUser.objects.filter(email=email).first()
            if existing_user:
                return JsonResponse({'error': 'A user with this email already exists'}, status=400)

            # Create a new CustomUser instance
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
            # Retrieve the JSON data from the request body
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            
            # Ensure 'email' and 'password' are present in the JSON data
            email = data.get('email')
            password = data.get('password')
            if email is None or password is None:
                return JsonResponse({'error': 'Missing email or password'}, status=400)
            
            try:
                # Retrieve the user based on the provided email
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
            # Check if the provided password matches the stored password
            if user.check_password(password):
                # Generate a unique token (UUID)
                try:
                    # Try to get the token
                    token = Token.objects.get(user_email=email)
                    # If the token exists, update it
                    token.token = uuid.uuid4().hex
                    token.save()
                except DoesNotExist:
                    # If the token does not exist, create it
                    token = Token(user_email=email, token=uuid.uuid4().hex)
                    token.save()
                
                return JsonResponse({'token': token.to_dict()}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
                
        

class Tracking(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsOwnerOrReadOnly]
    
    @csrf_exempt
    def start_tracking(request):
        user = TokenAuthentication().authenticate(request)

        if user is None:
            # Authentication failed
            raise AuthenticationFailed('Invalid token')
        
        if request.method == 'POST':            
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
                # Check if the product is already being tracked

                existing_product = TrackingRecord.objects.filter(user_email=email, product_url=url).allow_filtering().first()
                if existing_product:
                    return JsonResponse({'error': 'Product already being tracked'}, status=400)

                # Create a new tracked product instance and save to the database
                tracked_product = TrackingRecord.create(user_email=email, product_url=url, stock_check_interval=int(stock_check_interval), tracked_word=tracked_word)
                tracked_product.save()

                return JsonResponse({'message': 'Product tracking started successfully','tracking_record_id': str(tracked_product.id)})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)


    def track_by_id(request, track_id):
        user = TokenAuthentication().authenticate(request)

        if user is None:
            # Authentication failed
            raise AuthenticationFailed('Invalid token')
        
        if request.method == 'GET':
            
            try:
                tracked_record = TrackingRecord.objects.get(id=track_id)
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
        user = TokenAuthentication().authenticate(request)

        if user is None:
            # Authentication failed
            raise AuthenticationFailed('Invalid token')
        
        if request.method == 'GET':
            try:
                tracked_records = TrackingRecord.objects.filter(user_email=email).allow_filtering()
                data = []
                for tracked_record in tracked_records:
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


    def stop_tracking(request):
        email = request.data.get('email')
        url = request.data.get('url')

        if not email or not url:
            return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp = secrets.token_hex(6)

        # Send OTP to user's email
        subject = "OTP for Stop Tracking"
        message = f"Your OTP for stopping tracking for URL {url} is: {otp}"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            # Handle exception if email sending fails
            return Response({'error': 'Failed to send OTP email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Store the OTP in the user's session for verification 
        # TODO: Expire Sessions SESSION_COOKIE_AGE in setting
        request.session['stop_tracking_otp'] = otp
        request.session['stop_tracking_email'] = email
        request.session['stop_tracking_url'] = url

        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)


    def stop_tracking_confirm(request):
        otp = request.data.get('otp')

        if not otp:
            return Response({'error': 'Missing OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP
        if 'stop_tracking_otp' not in request.session or request.session['stop_tracking_otp'] != otp:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_401_UNAUTHORIZED)

        email = request.session.pop('stop_tracking_email')
        url = request.session.pop('stop_tracking_url')

        # Stop tracking
        try:
            tracking_record = TrackingRecord.objects.get(user_email=email, product_url=url)
            tracking_record.is_active = False
            tracking_record.save()
            return Response({'message': 'Tracking stopped successfully'}, status=status.HTTP_200_OK)
        except TrackingRecord.DoesNotExist:
            return Response({'error': 'Tracking record not found'}, status=status.HTTP_404_NOT_FOUND)


    def stop_track_by_id(request, track_id):
        if request.method == 'POST':
            try:
                # Find the tracking record by its ID
                tracking_record = TrackingRecord.objects.get(id=track_id)

                # Deactivate the tracking record
                tracking_record.is_active = False
                tracking_record.save()

                return JsonResponse({'message': 'Tracking stopped successfully'}, status=200)
            except TrackingRecord.DoesNotExist:
                return JsonResponse({'error': 'Tracking record not found'}, status=404)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)

