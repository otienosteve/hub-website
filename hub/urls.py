from django.urls import path

from . import views
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
import os

def debug_storage(request):
    return JsonResponse({
        "settings_module": os.environ.get("DJANGO_SETTINGS_MODULE"),
        "default_storage": type(default_storage).__name__,
        "STORAGES_default": settings.STORAGES["default"]["BACKEND"],
    })

app_name = "hub"

urlpatterns = [
    path("", views.home, name="home"),
    path("courses/", views.course_list, name="course_list"),
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
    path("events/", views.event_list, name="event_list"),
    path("events/<slug:slug>/", views.event_detail, name="event_detail"),
    path("about/", views.about, name="about"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("media/", views.media_list, name="media_list"),
    path("media/<int:pk>/", views.media_detail, name="media_detail"),
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("subscribe/", views.subscribe, name="subscribe"),
]


urlpatterns += [path("debug-storage/", debug_storage)]