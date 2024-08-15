from rest_framework import serializers
from .models import CustomUser, Profile
import re
import uuid
from .models import *
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, min_length=8, write_only=True)
    confirm_password = serializers.CharField(required=True, min_length=8, write_only=True)
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'role']
    
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return value
    
    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("The passwords do not match.")
        return data
    
    def create(self, validated_data):
        # Remove the confirm_password field before creating the user
        validated_data.pop('confirm_password', None)
        
        # Generate a UUID for the user
        user_id = uuid.uuid4()
        
        # Create the user
        user = CustomUser.objects.create_user(id=user_id, **validated_data)
        
        # Create the profile for the user
        Profile.objects.create(
            user=user,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Create Parent or Child based on role
        if user.role == 'parent':
            Parent.objects.create(user=user)
        elif user.role == 'child':
            pass
        
        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(style={'input_type':'password'}, write_only=True)

class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['id', 'user', 'profile', 'parent']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('first_name','last_name', 'age', 'gender')

