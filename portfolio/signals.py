import logging

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth.models import Permission
from django.contrib.auth.signals import (user_logged_in, user_logged_out,
                                         user_login_failed)
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User

# Get an instance of a logger
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):

    permission1 = Permission.objects.get(name="Can view user")
    permission2 = Permission.objects.get(name="Can change user")
    if created and instance.is_active:
        if instance.is_staff == False:
            instance.is_staff = True
            instance.save()
    else:
        instance.user_permissions.add(permission1)
        instance.user_permissions.add(permission2)
        

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get(model="logentry").id,
        object_id=request.user.id,
        object_repr=request.user.username,
        action_flag=ADDITION if user_logged_in else CHANGE,
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    logger.info("user logged in failed")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get(model="logentry").id,
        object_id=request.user.id,
        object_repr=request.user.username,
        action_flag=DELETION if user_logged_out else CHANGE,
    )
