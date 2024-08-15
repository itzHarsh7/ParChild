from django.contrib import admin
from .models import *
# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id','username','email','first_name', 'last_name')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'email','first_name', 'last_name')

admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(Profile,ProfileAdmin)
admin.site.register(Parent)
admin.site.register(Child)
admin.site.register(VerificationCode)