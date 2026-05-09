from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, identifier, password=None, **extra_fields):
        """
        Users can register with either email or phone.
        The `identifier` can be either an email or phone.
        """
        if not identifier:
            raise ValueError('The identifier (email/phone) must be set')

        if '@' in identifier:
            email = self.normalize_email(identifier)
            extra_fields['email'] = email
        else:
            extra_fields['phone'] = identifier

        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        return self.create_user(email, password, **extra_fields)