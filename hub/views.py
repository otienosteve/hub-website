from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import SubscribeForm
from .models import (AboutSection, BlogPost, CoreValue, Course, Event, MediaItem, Project,
                     Subscriber, TeamMember)


def home(request):
    now = timezone.now()
    media = MediaItem.objects.filter(is_published=True)
    featured = list(media.filter(featured=True)[:3])
    if len(featured) < 3:  # top up with the latest items so the section is never empty
        extra = media.exclude(pk__in=[m.pk for m in featured])[: 3 - len(featured)]
        featured += list(extra)
    return render(request, "hub/home.html", {
        "courses": Course.objects.filter(is_published=True)[:3],
        "events": Event.objects.filter(is_published=True, date__gte=now)[:3],
        "media_items": featured,
        "posts": BlogPost.objects.filter(is_published=True)[:3],
    })


def course_list(request):
    return render(request, "hub/course_list.html", {"courses": Course.objects.filter(is_published=True)})


def course_detail(request, slug):
    course = get_object_or_404(Course.objects.prefetch_related("topics"), slug=slug, is_published=True)
    return render(request, "hub/course_detail.html", {"course": course})


def event_list(request):
    # Chronological (earliest first). Upcoming events come first, then past events.
    events = Event.objects.filter(is_published=True).order_by("date")
    now = timezone.now()
    upcoming = [e for e in events if (e.end_date or e.date) >= now]
    past = [e for e in events if (e.end_date or e.date) < now]
    return render(request, "hub/event_list.html", {"upcoming": upcoming, "past": past})


def event_detail(request, slug):
    event = get_object_or_404(Event.objects.prefetch_related("highlights"), slug=slug, is_published=True)
    return render(request, "hub/event_detail.html", {"event": event})


def blog_list(request):
    return render(request, "hub/blog_list.html", {"posts": BlogPost.objects.filter(is_published=True)})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    more = BlogPost.objects.filter(is_published=True).exclude(pk=post.pk)[:2]
    return render(request, "hub/blog_detail.html", {"post": post, "more": more})


def media_list(request):
    items = MediaItem.objects.filter(is_published=True)
    fmt = request.GET.get("format")
    if fmt in (MediaItem.PORTRAIT, MediaItem.LANDSCAPE):
        items = items.filter(orientation=fmt)
    else:
        fmt = ""
    return render(request, "hub/media_list.html", {"items": items, "fmt": fmt})


def media_detail(request, pk):
    item = get_object_or_404(MediaItem, pk=pk, is_published=True)
    return render(request, "hub/media_detail.html", {"item": item})


def portfolio(request):
    return render(request, "hub/portfolio.html", {"projects": Project.objects.filter(is_published=True)})


def about(request):
    return render(request, "hub/about.html", {
        "values": CoreValue.objects.all(),
        "team": TeamMember.objects.all(),
        "sections": AboutSection.objects.all(),
    })


@require_POST
def subscribe(request):
    form = SubscribeForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        sub, created = Subscriber.objects.get_or_create(
            email=data["email"].lower(),
            defaults={"name": data["name"], "wants_membership": data["wants_membership"]})
        if not created:
            sub.name = data["name"] or sub.name
            sub.wants_membership = sub.wants_membership or data["wants_membership"]
            sub.save()
        messages.success(request, "You're on the list. We'll be in touch soon.")
    else:
        messages.error(request, "Please enter a valid email address.")
    nxt = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        nxt = reverse("hub:home")
    return redirect(f"{nxt}#join")
