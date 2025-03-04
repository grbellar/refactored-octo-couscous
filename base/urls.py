from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("impersonate/", include('impersonate.urls')),
    path("", include("pages.urls")),
    path("", include("exams.urls")),
    path("", include("payments.urls")),
    path("", include("review.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns