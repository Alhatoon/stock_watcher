# views.py
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from .models import TrackingRecord
from .serializers import TrackingRecordSerializer
import random
import string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from .permissions import IsOwnerOrReadOnly

import secrets
import logging

logger = logging.getLogger(__name__)



class UserLogin(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        if user:
            # Generate or retrieve token
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserRegistration(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Create user
        user = User.objects.create_user(username=username, password=password)
        if user:
            # Generate token for new user
            token = Token.objects.create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Failed to create user'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly])
@csrf_exempt
def start_tracking(request):
    if request.method == 'POST':
        # Get parameters from request
        email = request.POST.get('email')
        url = request.POST.get('url')
        stock_check_interval = request.POST.get('stock_check_interval')
        tracked_word = request.POST.get('tracked_word')

        # Validate input parameters
        if not email or not url or not stock_check_interval or not tracked_word:
            return JsonResponse({'error': 'Missing parameters'}, status=400)

        try:
            # Check if the product is already being tracked
            existing_product = TrackingRecord.objects.filter(user_email=email, product_url=url).first()
            if existing_product:
                return JsonResponse({'error': 'Product already being tracked'}, status=400)

            # Create a new tracked product instance and save to the database
            tracked_product = TrackingRecord(user_email=email, product_url=url, stock_check_interval=int(stock_check_interval), tracked_word=tracked_word)
            tracked_product.save()

            return JsonResponse({'message': 'Product tracking started successfully','tracking_record_id': str(tracked_product.id)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly])
@csrf_exempt
def track_by_id(request, track_id):
    if request.method == 'GET':
        try:
            tracked_record = TrackingRecord.objects.get(id=track_id)
            data = {
                'id': tracked_record.id,
                'user_id': tracked_record.user_id,
                'product_url': tracked_record.product_url,
                'stock_check_interval': tracked_record.stock_check_interval,
                'tracked_word': tracked_record.tracked_word
            }
            return JsonResponse(data)
        except TrackingRecord.DoesNotExist:
            return JsonResponse({'error': 'Tracking record not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly])
@csrf_exempt
def track_by_email(request, email):
    if request.method == 'GET':
        try:
            tracked_records = TrackingRecord.objects.filter(user_id=email)
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



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly])
@csrf_exempt
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

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly])
@csrf_exempt
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
        tracking_record = TrackingRecord.objects.get(user__email=email, product_url=url)
        tracking_record.is_active = False
        tracking_record.save()
        return Response({'message': 'Tracking stopped successfully'}, status=status.HTTP_200_OK)
    except TrackingRecord.DoesNotExist:
        return Response({'error': 'Tracking record not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly])
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

