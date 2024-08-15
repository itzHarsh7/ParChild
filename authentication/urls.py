from django.urls import path
from .views import *
urlpatterns = [
    path('register/',UserRegistrationAPIView.as_view()),
    path('login/',UserLoginAPIView.as_view()),
    path('child-register/',ChildRegistrationAPIView.as_view()),
    path('verify-code/',VerifyChildLoginAPIView.as_view()),
    path('logout/',UserLogoutAPIView.as_view())
]