from django.contrib.auth.models import AbstractUser
from shared.models import Base
from django.db import models

ORDINARY_USER, MANAGER, ADMIN = ("ordinary_user", "manager", "admin")
VIA_EMAIL, VIA_NUMBER = ("via_email", "via_number")
NEW, CODE_VERIFIED, DONE, PHOTO = ("new", "code_verified", "done", "photo")

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
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
