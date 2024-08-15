from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
import uuid
from django.utils import timezone


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ROLE_CHOICES = (
        ('parent', 'Parent'),
        ('child', 'Child'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='parent',null=False, blank=False)

    def __str__(self):
        return self.username
    
class Profile(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, null=True, blank=True)
    
class Parent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='parent')
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True)  # Link with Profile if needed

    def __str__(self):
        return f'{self.user.username}'

    
class VerificationCode(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f'{self.user.username} - {self.code}'
   

class Child(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='child')
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True)
    allowed_categories = models.ManyToManyField('parentapis.Category', related_name='children')