from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from shared.models import Base
from django.db import models
import random
import uuid

ORDINARY_USER, MANAGER, ADMIN = ('ordinary_user', 'manager', 'admin')
VIA_EMAIL, VIA_NUMBER = ('via_email', 'via_number')
NEW, CODE_VERIFIED, DONE, PHOTO = ('new', 'code_verified', 'done', 'photo')

class User(Base, AbstractUser):
    USER_ROLE = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN),
    )
    AUTH_TYPE = (
        (VIA_NUMBER, VIA_NUMBER),
        (VIA_EMAIL, VIA_EMAIL),
    )
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO, PHOTO),
    )

    user_role = models.CharField(max_length=20, choices=USER_ROLE, default=ORDINARY_USER)
    auth_type = models.CharField(max_lenght=20, choices=AUTH_TYPE)
    auth_status = models.CharField(max_lenght=20, choices=AUTH_STATUS, default=NEW)
    phone_number = models.CharField(max_lenght=17, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    @property
    def fullname(self):
        return f'{self.first_name} {self.last_name}'

    def create_code(self, auth_type):
        code = ''.join([str(random.ranint(0,9)) for _ in range(4)])
        UserConfirmation.objects.create(
            user=self,
            code=code,
            auth_type=auth_type
        )

        return code

    def check_username(self):
        if not self.username:
            temporary_username = f'slave_{uuid.uuid4().__str__().split('-')[-1]}'
            self.username = temporary_username

    def check_pass(self):
        if not self.password:
            temporary_password = f'{uuid.uuid4().__str__().split('-')[-1]}'
            self.password = temporary_password

    def check_passwords_hash(self):
        if not self.password.startswith('pbkdf'):
            self.password = make_password(self.password)

    def check_email(self):
        if self.email:
            self.email = self.email.lower()
    
    def token(self):
        refresh = RefreshToken.for_user(self)

        return {
            'refresh' : str(refresh),
            'access' : str(refresh.access_token)
        }

    def clean(self) -> None:
        self.check_username()
        self.check_pass()
        self.check_passwords_hash()
        self.check_email()
    
    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)

PHONE_EXPIRE = 2
EMAIL_EXPIRE = 5

class UserConfirmation(Base):
    AUTH_TYPE = (
        (VIA_NUMBER, VIA_NUMBER),
        (VIA_EMAIL, VIA_EMAIL),
    )

    auth_type = models.CharField(max_length=20, choices=AUTH_TYPE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    expiration_time = models.DateTimeField()
    has_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expiration_time:
            if self.auth_type == VIA_NUMBER:
                self.expiration_time = timezone.now() + timezone.timedelta(minutes=PHONE_EXPIRE)
            elif self.auth_type == VIA_EMAIL:
                self.expiration_time = timezone.now() + timezone.timedelta(minutes=EMAIL_EXPIRE)

            super(UserConfirmation, self).save(*args, **kwargs)
