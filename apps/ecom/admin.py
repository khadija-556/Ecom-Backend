from django.contrib import admin
from .models import *

@admin.register(CustomUser)

class CustomUserAdmin(admin.ModelAdmin):
    
    list_display = ('first_name','last_name','email','phone','user_status')
    search_fields = ('first_name','last_name','email','phone')

