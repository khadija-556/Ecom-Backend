from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager
from django.utils.text import slugify
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError

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
    subcategory = models.ForeignKey('SubCategory', on_delete=models.DO_NOTHING, related_name='products', blank=True, null=True)
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
    
    def __str__(self):
        return self.title


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            suffix = 1

            while SubCategory.objects.filter(slug=unique_slug).exclude(id=self.id).exists():
                unique_slug = f"{base_slug}-{suffix}"
                suffix += 1
            
            self.slug = unique_slug
            if self.pk:  
                original = SubCategory.objects.get(pk=self.pk)
                self.slug = original.slug

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Attribute(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='product_attribute')

    def __str__(self):
        return f"{self.product.title} for {self.attribute.title}"
    

class AttributeValue(models.Model):
    product_attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('flat', 'Flat'),
    )
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, blank=True, null=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_start = models.DateTimeField(blank=True, null=True)
    discount_end = models.DateTimeField(blank=True, null=True)

    def clean(self):
        if self.regular_price is None:
            return

        if self.discount_type == 'percentage':
            if self.discount_value is not None and self.discount_value > 100:
                raise ValidationError({
                    "discount_value": "Percentage discount cannot exceed 100."
                })

        if self.discount_type == 'flat':
            if self.discount_value is not None and self.discount_value > self.regular_price:
                raise ValidationError({
                    "discount_value": "Flat discount cannot exceed regular price."
                })
            
    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)



    @property
    def final_price(self):

        if self.regular_price is None:
            return Decimal('0')
        
        now = timezone.now()

        if self.discount_start and now < self.discount_start:
            return self.regular_price

        if self.discount_end and now > self.discount_end:
            return self.regular_price
        
        if not self.discount_type or self.discount_value is None:
            return self.regular_price

        # flat discount
        if self.discount_type == 'flat':
            return max(
                Decimal('0'),
                self.regular_price - self.discount_value
            )

        # percentage discount
        if self.discount_type == 'percentage':
            return self.regular_price - (
                self.regular_price * self.discount_value / Decimal('100')
            )

        return self.regular_price
    
    def __str__(self):
        return f"{self.product_attribute.product.title} - Regular Price: {self.regular_price} - Final Price: {self.final_price}"


######## General Settings API ##########

class GeneralSettings(models.Model):
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    tikTok_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    promotion_image = models.ImageField(upload_to='promotions/', blank=True, null=True)
    banner_image_1 = models.ImageField(upload_to='banners/', blank=True, null=True)
    banner_image_2 = models.ImageField(upload_to='banners/', blank=True, null=True)
    banner_image_3 = models.ImageField(upload_to='banners/', blank=True, null=True)


    def __str__(self):
        return "General Settings"
