from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager
from django.utils.text import slugify

# Create your models here.

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length = 255)
    last_name = models.CharField(max_length = 255)
    email = models.EmailField(unique = True, blank=True, null=True)
    phone = models.CharField (max_length = 25, unique = True, blank=True, null=True)
    STATUS_CHOICES = (
        ('active','Active'),
        ('inactive','Inactive'),
        ('blocked','Blocked'),
    )
    user_status = models.CharField(max_length = 20,choices = STATUS_CHOICES, default='active')
    photo_url = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)

    objects = CustomUserManager() # type: ignore

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return self.email if self.email else self.phone


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
    thumbnail = models.ImageField(upload_to='product_thumbnails/', blank=True, null=True)
    long_description = models.TextField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            suffix = 1

            while Product.objects.filter(slug=unique_slug).exclude(id=self.id).exists():
                unique_slug = f"{base_slug}-{suffix}"
                suffix += 1

            self.slug = unique_slug

            if self.pk:  
                original = Product.objects.get(pk=self.pk)
                self.slug = original.slug

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title 

        
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image1 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image4 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image5 = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return f"Images for {self.product.title}"

class Category(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    show_in_nav = models.BooleanField(default=False)
    is_showcase = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            suffix = 1

            while Category.objects.filter(slug=unique_slug).exclude(id=self.id).exists():
                unique_slug = f"{base_slug}-{suffix}"
                suffix += 1

            self.slug = unique_slug

            if self.pk:  
                original = Category.objects.get(pk=self.pk)
                self.slug = original.slug

        return super().save(*args, **kwargs)




    


