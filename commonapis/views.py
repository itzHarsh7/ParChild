from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from parentapis.serializers import CategorySerializer
from authentication.serializers import ProfileSerializer
from parentapis.models import Category
from authentication.models import CustomUser, Profile
# Create your views here.
class Listcategory(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        categories = Category.objects.all()
        if not categories.exists():
            return Response({"message": "No categories available"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(categories, many=True)
        return Response({"status":True,"data":serializer.data},status=status.HTTP_200_OK)
    
class ListProfile(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,pk):
        user = CustomUser.objects.filter(id=pk).first()
        print(user)
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfileSerializer(profile)
        return Response({"status":True,"data":serializer.data}, status=status.HTTP_200_OK)