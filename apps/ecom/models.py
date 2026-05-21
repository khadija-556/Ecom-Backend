from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager

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

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return self.email if self.email else self.phone





        


