from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

"""Define URL patterns for the entire application."""
urlpatterns = [
    path("api/", include("apps.cdr.urls")),
]

"""Check if the application is in debug mode."""
if settings.DEBUG:
    from django.conf.urls.static import static

    """Add URL pattern for accessing the Django admin site and schema."""
    urlpatterns += [
        path("admin/", admin.site.urls),
        path("schema/", SpectacularAPIView.as_view(), name="schema"),
        path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
        path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    ]

    # Static and media files URLs for development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    """Customize Django admin interface titles."""
    admin.site.site_header = 'AVA'
    admin.site.site_title = 'AVA Administration'
    admin.site.index_title = 'Welcome To AVA Administration'
