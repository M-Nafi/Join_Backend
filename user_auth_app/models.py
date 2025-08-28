from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .api.validators import validate_username_format, validate_phone_format


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=50,
        unique=True,
        validators=[validate_username_format],
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    phone = models.CharField(max_length=13, default="123456789", validators=[validate_phone_format])
    emblem = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    is_guest = models.BooleanField(default=False)
    last_activity = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def update_activity(self):
        """
        Updates the last activity timestamp of the user.
        """
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    def save(self, *args, **kwargs):
        """
        Saves the user model instance.

        If the username is 'guest', sets the user's password to an unusable password
        so that the user can't log in with a password.

        :param args: Positional arguments to pass to the superclass's save method
        :param kwargs: Keyword arguments to pass to the superclass's save method
        """
        if self.username == "guest":
            self.set_unusable_password()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a string representation of the user instance.

        The string representation is the user's email address.

        :return: A string representation of the user instance
        :rtype: str
        """
        return self.email