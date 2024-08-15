from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser, Parent, Child, Profile
from django.shortcuts import get_object_or_404
from .serializers import *
from .utils import *
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import *
from django.db import transaction
from datetime import datetime
import random
from django.core.mail import send_mail
from django.conf import settings


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    access_token['username'] = user.username
    access_token['email'] = user.email
    access_token['first_name'] = user.first_name
    access_token['last_name'] = user.last_name
    return {
        'refresh': str(refresh),
        'access': str(access_token),
    }

class UserRegistrationAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.save()
            user_details = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role
            }
            email_subject = 'Welcome'
            email_message = f'Welcome {user.first_name}!. Thanks for registering. Enjoying the benefits of YoutubeKids Filtered Application'
            # send_mail(email_subject, email_message, settings.EMAIL_HOST_USER, [user.email])
            return Response({"message":"Registeration Successful","status": True, "User_Details": user_details}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChildRegistrationAPIView(APIView):
    permission_classes = [IsAuthenticated, IsParent]

    def post(self, request):
        if request.user.role != 'parent':
            return Response({"message": "Only parents can create child accounts."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserRegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            parent = Parent.objects.get(user=request.user)
            user_details = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role
            }
            profile = Profile.objects.get(user=user)
            print(user_details)
            print()
            print(profile)
            print(parent)
            child = Child.objects.create(
                user=user,
                parent=parent,
                profile=profile
            )
            email_subject = 'Child Registeration Successful'
            email_message = f'Welcome {request.user.first_name}!. You have successfully registered your child {user.first_name}.'
            # send_mail(email_subject, email_message, settings.EMAIL_HOST_USER, [request.user.email])
            return Response({"status": True, "User_Details": user_details}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginAPIView(APIView):
    permission_classes=[]
    authentication_classes = []

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                    if user.check_password(password):
                        if user.role == 'parent':
                            user = authenticate(request, username=user.username, password=password)
                            if user is not None:
                                login(request, user)
                                tokens = get_tokens_for_user(user)
                                welcome_message = f"Welcome, {user.first_name}!" if user.first_name else "Welcome, User!"
                                email_subject = 'Account Login Notification'
                                email_message = f'Your Account Logged In detected {datetime.now()}'
                                # send_mail(email_subject, email_message, 'from@example.com', [user.email])
                                response = Response({
                                "msg": welcome_message,
                                "status": True,
                                "User_Details": {
                                    "id": user.id,
                                    "username": user.username,
                                    "email": user.email,
                                    "first_name": user.first_name,
                                    "last_name": user.last_name
                                }
                            }, status=status.HTTP_200_OK)
                                response.set_cookie('access', tokens['access'], httponly=True, secure=True)
                                response.set_cookie('refresh', tokens['refresh'], httponly=True, secure=True)
                                return response
                            else:
                                return Response({"msg": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

                        elif user.role == 'child':
                            # Generate a verification code
                            verification_code = random.randint(100000, 999999)
                            verification_code = str(random.randint(100000, 999999))
                            VerificationCode.objects.create(user=user, code=verification_code)

                            # Send the verification code to the parent's email
                            child = Child.objects.get(user=user)
                            print(child)
                            print(child.parent)
                            if child and child.parent:
                                parent_email = child.parent.user.email
                                print(parent_email)
                                email_subject = 'Child Login Verification Code'
                                email_message = f'Your child is attempting to log in. Verification code: {verification_code}'
                                # send_mail(email_subject, email_message, settings.EMAIL_HOST_USER, [parent_email])

                            return Response({"message": "Verification code sent to parent's email.", "status": True}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message": "Incorrect Password!!!", "status": False}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message": "User does not exist", "status": False}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyChildLoginAPIView(APIView):
    permission_classes=[]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')
        
        if not email or not verification_code:
            return Response({"message": "Username and verification code are required.", "status": False}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(email=email).first()

        if user and user.role == 'child':
            verification_record = VerificationCode.objects.filter(user=user, code=verification_code).first()

            if verification_record and not verification_record.is_expired():
                verification_record.delete()
                login(request, user)
                tokens = get_tokens_for_user(user)
                welcome_message = f"Welcome {user.first_name}!"
                email_subject = 'Account Login Notification'
                email_message = f'Your Account Logged In detected {datetime.now()}'
                # send_mail(email_subject, email_message, settings.EMAIL_HOST_USER, [user.email])
                response = Response({
                    "msg": welcome_message,
                    "status": True,
                    "User_Details": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name
                    }}, status=status.HTTP_200_OK)
                response.set_cookie('access', tokens['access'], httponly=True, secure=True)
                response.set_cookie('refresh', tokens['refresh'], httponly=True, secure=True)
                return response
            else:
                return Response({"message": "Invalid or expired verification code.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "User does not exist or is not a child.", "status": False}, status=status.HTTP_404_NOT_FOUND)
    
class UserLogoutAPIView(APIView):
    authentication_classes = []
    def get(self, request):
        logout(request)
        response = Response({"msg": "Successfully logged out.", "status": True}, status=status.HTTP_200_OK)
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        response.delete_cookie('csrftoken')
        response.delete_cookie('sessionid')
        return response