import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

# from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    ADMIN,Administrator,2025-04-24 10:38:17.920391,2025-04-24 10:38:17.920391
    SUB_USER,Subscribed user,2025-04-24 10:38:17.920391,2025-04-24 10:38:17.920391
    UNSUB_USER,Unsubscribed user,2025-04-24 10:38:17.920391,2025-04-24 10:38:17.920391
    ANONYMOUS,Anonymous user,2025-04-24 10:38:17.920391,2025-04-24 10:38:17.920391
    """

    def create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("Users must have an username")
        if not email:
            raise ValueError("Users must have an email address")
            # email = f"{username}-stub-email@stub-email.ru"
        if not password:
            raise ValueError("Users must have an password")
            # password = username
            # raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(username=username, role_code="ADMIN")
        user_cred = UserCred(user=user, email=email, password=password)
        # user_cred.set_password(password)
        user.save()
        user_cred.save()
        return user

    def create_superuser(self, username, email=None, password=None):
        user = self.create_user(username, email=email, password=password)
        # user.is_admin = True
        user.save()
        return user

    # def create_superuser(self, username, email, password=None, **extra_fields):
    #     extra_fields.setdefault('is_staff', True)
    #     extra_fields.setdefault('is_superuser', True)

    #     if extra_fields.get('is_staff') is not True:
    #         raise ValueError(_('Superuser must have is_staff=True.'))
    #     if extra_fields.get('is_superuser') is not True:
    #         raise ValueError(_('Superuser must have is_superuser=True.'))

    #     return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    role_code = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # user_cred = models.OneToOneField(
    #     'UserCred',
    #     on_delete=models.CASCADE,
    #     related_name='user',
    #     null=True,
    # )
    password = None
    last_login = None

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = '"profile"."user"'
        managed = False

    def __str__(self):
        return self.username

    def get_email(self):
        return self.user_cred.email if self.user_cred else None

    @property
    def email(self):
        return self.get_email()


class UserCred(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_cred",
        primary_key=True,
    )

    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"profile"."user_cred"'
        managed = False

    def __str__(self):
        return self.email

    # def set_password(self, raw_password):
    #     from django.contrib.auth.hashers import make_password
    #     self.password = make_password(raw_password)
    #     self.save()

    # def check_password(self, raw_password):
    #     from django.contrib.auth.hashers import check_password
    #     return check_password(raw_password, self.password)
