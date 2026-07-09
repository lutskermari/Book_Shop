from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Phone Number"))
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name=_("Avatar"))

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.username