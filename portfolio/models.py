from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinLengthValidator
from django.db import models


class User(AbstractUser):
    """
    Extended user model with mentioned fields.
    """

    phone_number = models.CharField(
        max_length=15, null=True, blank=True, validators=[MinLengthValidator(10)]
    )
    home_address = models.TextField(max_length=500, blank=True)
    location = gis_models.PointField(
        geography=True, spatial_index=True, blank=True, null=True
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
