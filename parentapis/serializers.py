from rest_framework import serializers
from .models import NotAllowedSearches, Category
from authentication.models import Profile, Child
from authentication.serializers import ProfileSerializer
class NotAllowedSearchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotAllowedSearches
        fields = ['searches', 'created_at']

class childprofileupdateserializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    allowed_categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)
    class Meta:
        model = Child
        fields = ['profile', 'allowed_categories']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields=['id','name']