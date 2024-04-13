from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        self.save(user, commit=True)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if password is None:
            raise ValueError('Superusers must have a password')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, verbose_name='email')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    username = models.CharField(max_length=150, blank=True)  # Optional username field for compatibility
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    license_number = models.IntegerField(max_length=50, blank=True)
    date_start = models.DateField()
    date_and = models.DateField()
    phone_number = models.CharField(max_length=15)  # Telefon raqami
    verification_code = models.CharField(max_length=6)  # Tasdiqlash kodi
    def __str__(self):
        return self.email