import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from .models import (AboutSection, BlogPost, CoreValue, Course, CourseApplication, CourseOutcome,
                     CourseTopic, Event, EventHighlight, MediaItem, Project, SiteSettings,
                     Subscriber, TeamMember)


def thumb(obj, field, size=44):
    f = getattr(obj, field)
    if not f:
        return "–"
    return format_html('<img src="{}" style="height:{}px;width:{}px;object-fit:cover;border-radius:6px">',
                       f.url, size, size)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Identity", {"fields": ["org_name", "tagline"]}),
        ("Home page banner", {"fields": ["hero_headline", "hero_subheadline", "hero_banner"]}),
        ("Our story (home page)", {"fields": ["story_title", "story"]}),
        ("About page", {"fields": ["mission", "vision"]}),
        ("Contact", {"fields": ["contact_email", "phone", "location"]}),
        ("Social links", {"fields": ["linkedin_url", "x_url", "youtube_url", "github_url", "instagram_url"]}),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Skip the list screen: there is only ever one settings record.
        from django.shortcuts import redirect
        obj = SiteSettings.load()
        return redirect("admin:hub_sitesettings_change", obj.pk)


class CourseTopicInline(admin.StackedInline):
    model = CourseTopic
    extra = 3
    fields = ["title", "description", "order"]


class CourseOutcomeInline(admin.StackedInline):
    model = CourseOutcome
    extra = 2
    fields = ["title", "description", "order"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "price", "duration_display", "next_cohort_date", "is_published", "order"]
    list_editable = ["is_published", "order"]
    list_filter = ["is_published"]
    search_fields = ["title", "summary"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CourseTopicInline, CourseOutcomeInline]
    fieldsets = [
        (None, {"fields": ["title", "slug", "summary", "cover"]}),
        ("Schedule and pricing", {"fields": ["duration_days", "price", "next_cohort_date", "payment_url"]}),
        ("Prerequisites", {"fields": ["prerequisites"]}),
        ("Publishing", {"fields": ["is_published", "order"]}),
    ]


@admin.register(CourseApplication)
class CourseApplicationAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "course", "email", "python_proficiency", "created_at"]
    list_filter = ["course", "python_proficiency", "created_at"]
    search_fields = ["first_name", "last_name", "email", "phone_number", "county", "institution_company"]
    readonly_fields = [
        "course", "first_name", "last_name", "email", "phone_number", "county",
        "current_occupation", "institution_company", "python_proficiency", "created_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class EventHighlightInline(admin.TabularInline):
    model = EventHighlight
    extra = 4
    fields = ["text", "order"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["photo_preview", "title", "date", "location", "tags", "is_published"]
    list_display_links = ["title"]
    list_editable = ["is_published"]
    list_filter = ["is_published", "date"]
    search_fields = ["title", "description", "tags"]
    date_hierarchy = "date"
    prepopulated_fields = {"slug": ("title",)}
    inlines = [EventHighlightInline]
    fieldsets = [
        (None, {"fields": ["title", "slug", "description", "tags"]}),
        ("When and where", {"fields": ["date", "end_date", "location", "registration_url"]}),
        ("Images", {"fields": ["banner", "photo"]}),
        ("Publishing", {"fields": ["is_published"]}),
    ]

    @admin.display(description="Photo")
    def photo_preview(self, obj):
        return thumb(obj, "photo")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "date", "is_published"]
    list_editable = ["is_published"]
    list_filter = ["is_published", "date"]
    search_fields = ["title", "author", "description", "content"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "date"


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ["thumb_preview", "name", "platform", "orientation", "featured", "date", "is_published"]
    list_display_links = ["name"]
    list_editable = ["featured", "is_published"]
    list_filter = ["orientation", "platform", "featured", "is_published"]
    search_fields = ["name", "description"]

    @admin.display(description="Cover")
    def thumb_preview(self, obj):
        return thumb(obj, "thumbnail")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "client", "year", "is_published", "order"]
    list_editable = ["is_published", "order"]
    search_fields = ["title", "client", "description"]


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["photo_preview", "name", "role", "order"]
    list_display_links = ["name"]
    list_editable = ["order"]

    @admin.display(description="Photo")
    def photo_preview(self, obj):
        return thumb(obj, "photo")


admin.site.register(CoreValue, type("CoreValueAdmin", (admin.ModelAdmin,), {
    "list_display": ["title", "order"], "list_editable": ["order"]}))
admin.site.register(AboutSection, type("AboutSectionAdmin", (admin.ModelAdmin,), {
    "list_display": ["title", "order"], "list_editable": ["order"]}))


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "wants_membership", "created_at"]
    list_filter = ["wants_membership", "created_at"]
    search_fields = ["email", "name"]
    actions = ["export_csv"]

    @admin.action(description="Export selected subscribers to CSV")
    def export_csv(self, request, queryset):
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="subscribers.csv"'
        w = csv.writer(resp)
        w.writerow(["email", "name", "wants_membership", "joined"])
        for s in queryset:
            w.writerow([s.email, s.name, s.wants_membership, s.created_at.date()])
        return resp
