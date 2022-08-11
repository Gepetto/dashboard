from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("gh/", include("gh.urls")),
    path("", include("rainboard.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
