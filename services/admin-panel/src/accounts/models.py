import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class UserManager(BaseUserManager):
    """
    ADMIN,Administrator,2025-04-24 10:38:17.920391,2025-04-24 10:38:17.920391
    SUB_USER,Subscribed user,2025-04-24 10:38:17.920391,2025-04-24 10:38:17.920391
    UNSUB_USER,Unsubscribed user,2025-04-24 10:38:17.920391,2025-04-24 10:38:17.920391
    ANONYMOUS,Anonymous user,2025-04-24 10:38:17.920391,2025-04-24 10:38:17.920391
    """

    def create_user(
        self,
        username,
        email,
        password,
        role_code="UNSUB_USER",
    ):
        if not username:
            raise ValueError("Users must have an username")
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have an password")
        email = self.normalize_email(email)
        user = self.model(username=username, role_code=role_code)
        user_cred = UserCred(user=user, email=email)
        user_cred.set_password(password)
        user.save(using=self._db)
        user_cred.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None):
        return self.create_user(
            username=username,
            email=email,
            password=password,
            role_code="ADMIN",
        )


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    role_code = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    def set_password(self, password):
        self.password = pwd_context.hash(password)

    def check_password(self, password):
        return pwd_context.verify(password, self.password)
