from django.contrib import admin
from django.urls import path
from django.conf import settings
from app.views import view_upload_test, view_get_file

urlpatterns = [
    path('admin/', admin.site.urls),
    path('view/<slug:bucket>/<slug:token>', view_upload_test, name='view-upload'),
    path('view', view_get_file, name='view-get'),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)
