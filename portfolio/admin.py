import json

from django.contrib import admin
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.shortcuts import render
from django.urls import NoReverseMatch, path, reverse
from django.utils.encoding import force_str
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from mapwidgets.widgets import GooglePointFieldWidget

from .models import User

action_names = {
    ADDITION: pgettext_lazy("logentry_admin:action_type", "Logged In"),
    DELETION: pgettext_lazy("logentry_admin:action_type", "Logged Out"),
    CHANGE: pgettext_lazy("logentry_admin:action_type", "Change"),
}


class ActionListFilter(admin.SimpleListFilter):
    title = _("action")
    parameter_name = "action_flag"

    def lookups(self, request, model_admin):
        return action_names.items()

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(action_flag=self.value())
        return queryset


class LogEntryAdmin(admin.ModelAdmin):
    """
    To show the log entries only to the superusers.
    """

    list_display_links = ["action_time", "action_description"]

    list_display = [
        "user_link",
        "content_type",
        "action_description",
        "action_time",
    ]

    def get_actions(self, request):
        actions = super(LogEntryAdmin, self).get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    def action_description(self, obj):
        return action_names[obj.action_flag]

    action_description.short_description = _("action")

    def user_link(self, obj):
        content_type = ContentType.objects.get_for_model(type(obj.user))
        user_link = escape(force_str(obj.user))
        try:
            # try returning an actual link instead of object repr string
            url = reverse(
                "admin:{}_{}_change".format(content_type.app_label, content_type.model),
                args=[obj.user.pk],
            )
            user_link = '<a href="{}">{}</a>'.format(url, user_link)
        except NoReverseMatch:
            pass
        return mark_safe(user_link)

    user_link.admin_order_field = "user"
    user_link.short_description = _("user")


# class PointAdmin(admin.ModelAdmin):
#     """
#     To show the map in the point model.
#     """

#     model = Point
#     formfield_overrides = {models.PointField: {"widget": GooglePointFieldWidget()}}


def viewMap(request):
    """
    Views to show details of the user on the map location popup.
    """
    template_name = "profile.html"
    users = User.objects.all()
    all_users = []
    for user in users:
        if user.location is not None:
            user_details = [
                user.username,
                user.location.location.coords[0],
                user.location.location.coords[1],
                int(user.phone_number) if user.phone_number else '',
                user.home_address,
            ]
            all_users.append(user_details)
    context = {"users": json.dumps(all_users)}
    return render(request, template_name, context)


class UserAdmin(admin.ModelAdmin):
    """
    To show user details.
    """
    model = User
    formfield_overrides = {models.PointField: {"widget": GooglePointFieldWidget()}}

    list_display = [
        "username",
        "email",
        "location",
        "home_address",
        "phone_number",
        "is_staff",
        "is_superuser",
    ]

    change_list_template = "admin/change_list.html"

    _readonly_fields = (
        "is_superuser",
        "user_permissions",
        "groups",
        "date_joined",
        "is_active",
        "last_login",
    )

    def get_readonly_fields(self, request, obj):
        if not request.user.is_superuser:
            return self._readonly_fields
        return super().get_readonly_fields(request, obj)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id:
            user = User.objects.filter(id=object_id).first()
            if user.is_active and not user.is_staff:
                user.is_staff = True
                user.save()
            else:
                permission1 = Permission.objects.get(name="Can change user")
                permission2 = Permission.objects.get(name="Can view user")
                user.user_permissions.add(permission1, permission2)
        return self._changeform_view(request, object_id, form_url, extra_context)

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(pk=request.user.pk)

    def get_urls(self):
        urls = super(UserAdmin, self).get_urls()
        my_urls = [path("viewmap", viewMap, name="viewmap")]
        return my_urls + urls


admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(User, UserAdmin)
