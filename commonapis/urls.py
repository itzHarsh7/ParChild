from django.urls import path
from .views import *
urlpatterns =[
    path('category/', Listcategory.as_view()),
    path('profile/<str:pk>/', ListProfile.as_view()),
]