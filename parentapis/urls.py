from django.urls import path
from .views import *
urlpatterns = [
    path('historyNA/<str:pk>/', NotAllowedSearchAPIView.as_view()),
    path('update-child/<str:child_id>/', UpdateChildsProfileAPIView.as_view()),
    path('category-add/', AddCustomCategory.as_view()),
]