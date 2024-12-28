from django.urls import path, include

urlpatterns = [
    path("", include("apps.cdr.urls.cdr.urls_cdr")),
]

