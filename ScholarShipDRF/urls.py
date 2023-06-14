
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('rest-api/', include('rest_framework.urls')),
    path('api/', include('scholarshipback.urls')),
    path('', include('scholarshipfront.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
