from drf_yasg.views import get_schema_view
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Authentication API",
        default_version='v1',
        description="",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('user-api/', include("user.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root = settings.MEDIA_ROOT
    )
