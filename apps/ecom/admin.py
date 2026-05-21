from django.contrib import admin
from .models import *

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    
    list_display = ('first_name','last_name','email','phone','user_status')
    search_fields = ('first_name','last_name','email','phone')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title','product_code','product_status','product_type')
    search_fields = ('title','slug','product_code')
    ordering = ('-created_at',)
    list_filter = ('product_status','product_type')

