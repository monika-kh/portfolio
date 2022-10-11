from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django_registration.backends.one_step.views import RegistrationView
from portfolio.forms import UserForm

urlpatterns = [
    path("", include(("portfolio.urls", "portfolio"), namespace="portfolio")),
    path(
        r"register/",
        RegistrationView.as_view(form_class=UserForm),
        name="django_registration_register",
    ),
    path("admin/", admin.site.urls),
    path("", include("django_registration.backends.one_step.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
