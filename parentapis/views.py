from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from authentication.permissions import IsParent
from authentication.serializers import ProfileSerializer
from authentication.models import CustomUser,Child,Profile
from .models import NotAllowedSearches,Category
from .serializers import NotAllowedSearchesSerializer,CategorySerializer
from django.shortcuts import get_object_or_404


# Create your views here.
class NotAllowedSearchAPIView(APIView):
    permission_classes = [IsAuthenticated, IsParent]
    def get(self,request,pk):
        try:
            child = get_object_or_404(CustomUser, id=pk)
            searches = NotAllowedSearches.objects.filter(user=child)
            if not searches.exists():
                return Response({"message":"No Search Found"}, status=status.HTTP_200_OK)
            serializer = NotAllowedSearchesSerializer(searches, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "An error occurred while processing your request."},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UpdateChildsProfileAPIView(APIView):
    permission_classes = [IsAuthenticated,IsParent]

    def patch(self, request,child_id):
        user = request.user
        print(user)
        child = CustomUser.objects.filter(id=child_id).first()
        print(child)
        child = Child.objects.get(user=child)
        print(child.parent.user.username)
        if child.parent.user != user:
            return Response({"message":"You are not allowed to change the profile of some other child","status":False}, status=status.HTTP_403_FORBIDDEN)
        print('Jinga Lala HU HU')
        data=request.data
        profile_data = data.get('profile', {})
        allowed_categories = data.get('allowed_categories', [])
        if profile_data:
            try:
                profile = Profile.objects.get(user=child.user)
                for attr, value in profile_data.items():
                    if hasattr(profile, attr):
                        setattr(profile, attr, value)
                profile.save()
            except Profile.DoesNotExist:
                return Response({"message": "Profile not found", "status": False}, status=status.HTTP_404_NOT_FOUND)

        # Update allowed_categories if allowed_categories_ids is provided
        if allowed_categories:
            print(allowed_categories)
            try:
                allowed_categories = Category.objects.filter(id__in=allowed_categories)
                print(allowed_categories)
                child.allowed_categories.set(allowed_categories)
            except Category.DoesNotExist:
                return Response({"message": "One or more categories not found", "status": False}, status=status.HTTP_400_BAD_REQUEST)

        # Return a successful response
        return Response({"message":"Profile updated Successfully","status": True}, status=status.HTTP_200_OK)

class AddCustomCategory(APIView):
    permission_classes = [IsAuthenticated,IsParent]
    def post(self,request):
        name = request.data.get('name')
        Category.objects.create(name=name)
        return Response({"message":"Category Added Successfully!!","status": True}, status=status.HTTP_200_OK)