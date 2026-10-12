from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Agentic AI Hub · Admin"
admin.site.site_title = "Agentic AI Hub"
admin.site.index_title = "Manage your website content"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("hub.urls")),
]

# Uploaded images (banners, photos). For production, serve /media/ via nginx or object storage.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
