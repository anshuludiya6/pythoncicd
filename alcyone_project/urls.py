
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


schema_view = get_schema_view(
   openapi.Info(
      title="Alcyone Project",
      default_version='v1',
      description="Alcyone project api's.",
      # terms_of_service="https://www.google.com/policies/terms/",
      # contact=openapi.Contact(email="contact@snippets.local"),
      # license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   # authentication_classes=[]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentication/', include('Authentication.urls')),
    path('Users/', include('Users.urls')),
    path('swagger_doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
