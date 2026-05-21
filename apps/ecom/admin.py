from django.contrib import admin
from .models import *

@admin.register(CustomUser)

class CustomUserAdmin(admin.ModelAdmin):
    
    list_display = ('first_name','last_name','email','phone','user_status')
    search_fields = ('first_name','last_name','email','phone')

class Product(models.Model):
    product_code = models.CharField(max_length = 255)
    title = models.CharField(max_length = 255)
    ingredients = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    PRODUCT_TYPE_CHOICE = (
        ('single','Single'),
        ('variable','Variable'),
    )
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICE, default='single')
    PRODUCT_STATUS_CHOICES = (
        ('pending','Pending'),
        ('publish','Publish'),
    )
    product_status = models.CharField(max_length=20, choices=PRODUCT_STATUS_CHOICES, default='pending')
    long_description = models.TextField()
    short_description = models.TextField()
    PRODUCT_PRICE_CHOICES = (
        ('pending','Pending'),
        ('publish','Publish'),
    )
    created_at = models.DateTimeField(auto_now_add = True)
    update_at = models.DateTimeField(auto_now = True)