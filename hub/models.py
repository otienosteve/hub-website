import math
import re

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


# --------------------------------------------------------------------------- helpers
class SluggedModel(models.Model):
    """Adds an auto-generated, unique slug based on `slug_source`."""

    slug = models.SlugField(max_length=160, unique=True, blank=True,
                            help_text="Part of the page address. Leave blank to generate it from the title.")
    slug_source = "title"

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(getattr(self, self.slug_source))[:140] or "item"
            slug, n = base, 2
            while type(self).objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)


def split_tags(value):
    return [t.strip() for t in (value or "").split(",") if t.strip()]


# --------------------------------------------------------------------------- site-wide
class SiteSettings(models.Model):
    """One row only: the editable text that powers the home and about pages."""

    org_name = models.CharField("Organisation name", max_length=80, default="Agentic AI Hub")
    tagline = models.CharField(max_length=160, default="Learn to build AI that gets things done.")

    hero_headline = models.CharField(max_length=160, default="Build AI agents that do real work.")
    hero_subheadline = models.TextField(
        default="Hands-on courses, community events and open projects for people building agentic AI.")
    hero_banner = models.ImageField("Hero banner image", upload_to="site/", blank=True,
                                    help_text="Optional. Shown beside the headline on the home page. Landscape, at least 1400px wide.")

    story_title = models.CharField(max_length=120, default="Where agents go from demo to daily work")
    story = models.TextField(help_text="Short story of the organisation. Blank lines start a new paragraph.", blank=True)

    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)

    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)

    linkedin_url = models.URLField(blank=True)
    x_url = models.URLField("X / Twitter URL", blank=True)
    youtube_url = models.URLField("YouTube URL", blank=True)
    github_url = models.URLField("GitHub URL", blank=True)
    instagram_url = models.URLField("Instagram URL", blank=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def story_paragraphs(self):
        return [p.strip() for p in self.story.split("\n\n") if p.strip()]

    @property
    def social_links(self):
        pairs = [("LinkedIn", self.linkedin_url), ("X", self.x_url), ("YouTube", self.youtube_url),
                 ("GitHub", self.github_url), ("Instagram", self.instagram_url)]
        return [(n, u) for n, u in pairs if u]


# --------------------------------------------------------------------------- courses
class Course(SluggedModel):
    title = models.CharField(max_length=140)
    summary = models.TextField(help_text="Two or three sentences shown on the course card.")
    cover = models.ImageField(upload_to="courses/", blank=True, help_text="Optional cover image.")
    duration_days = models.PositiveIntegerField(
        help_text="Length in training days. Shown as weeks (5 days = 1 week) when longer than 5 days.")
    prerequisites = models.TextField(blank=True, help_text="One prerequisite per line. Leave blank if none.")
    next_cohort_date = models.DateField(null=True, blank=True,
                                        help_text="Leave blank to show “On request”.")
    enrol_url = models.URLField("Enrolment link", blank=True,
                                help_text="Optional. Where the Enrol button sends people. Defaults to the contact email.")
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("hub:course_detail", args=[self.slug])

    @property
    def duration_display(self):
        d = self.duration_days
        if d > 5:
            weeks = math.ceil(d / 5)
            return f"{weeks} week{'s' if weeks != 1 else ''}"
        return f"{d} day{'s' if d != 1 else ''}"

    @property
    def prerequisite_list(self):
        return [l.strip(" -•\t") for l in self.prerequisites.splitlines() if l.strip()]

    @property
    def next_cohort_display(self):
        if self.next_cohort_date and self.next_cohort_date >= timezone.localdate():
            return self.next_cohort_date
        return None


class CourseTopic(models.Model):
    course = models.ForeignKey(Course, related_name="topics", on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True, help_text="A sentence or two under the topic name.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


# --------------------------------------------------------------------------- events
class Event(SluggedModel):
    title = models.CharField(max_length=160)
    description = models.TextField()
    tags = models.CharField(max_length=200, blank=True, help_text="Comma separated, e.g. workshop, LLMs, Nairobi")
    date = models.DateTimeField(help_text="Start date and time.")
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=160, blank=True, help_text="Venue or “Online”.")
    banner = models.ImageField(upload_to="events/banners/", blank=True, help_text="Wide image for the event page.")
    photo = models.ImageField("Small photo", upload_to="events/photos/", blank=True,
                              help_text="Square thumbnail used on cards and lists.")
    registration_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("hub:event_detail", args=[self.slug])

    @property
    def tag_list(self):
        return split_tags(self.tags)

    @property
    def is_upcoming(self):
        return (self.end_date or self.date) >= timezone.now()


class EventHighlight(models.Model):
    event = models.ForeignKey(Event, related_name="highlights", on_delete=models.CASCADE)
    text = models.CharField(max_length=240)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text


# --------------------------------------------------------------------------- blog
class BlogPost(SluggedModel):
    title = models.CharField(max_length=180)
    date = models.DateField(default=timezone.localdate)
    author = models.CharField(max_length=100)
    description = models.TextField(help_text="Short summary shown on blog cards.")
    content = models.TextField(help_text="Full article. Blank lines start a new paragraph. "
                                         "Start a line with ## for a sub-heading.")
    banner = models.ImageField(upload_to="blog/", blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("hub:blog_detail", args=[self.slug])

    @property
    def blocks(self):
        """Content split into (kind, text) blocks for safe rendering."""
        out = []
        for raw in re.split(r"\n\s*\n", self.content.strip()):
            raw = raw.strip()
            if not raw:
                continue
            if raw.startswith("## "):
                out.append(("h2", raw[3:].strip()))
            else:
                out.append(("p", raw))
        return out

    @property
    def read_minutes(self):
        return max(1, round(len(self.content.split()) / 220))


# --------------------------------------------------------------------------- media
class MediaItem(models.Model):
    PORTRAIT, LANDSCAPE = "portrait", "landscape"
    ORIENTATIONS = [(PORTRAIT, "Portrait (vertical, e.g. Shorts, Reels, TikTok)"),
                    (LANDSCAPE, "Landscape (horizontal, e.g. YouTube)")]
    PLATFORMS = [("youtube", "YouTube"), ("tiktok", "TikTok"), ("instagram", "Instagram"),
                 ("linkedin", "LinkedIn"), ("x", "X / Twitter"), ("vimeo", "Vimeo"), ("other", "Other")]

    name = models.CharField(max_length=160)
    description = models.TextField()
    orientation = models.CharField(max_length=10, choices=ORIENTATIONS, default=LANDSCAPE)
    platform = models.CharField(max_length=12, choices=PLATFORMS, default="youtube")
    video_url = models.URLField("Link to the video")
    thumbnail = models.ImageField(upload_to="media/", blank=True,
                                  help_text="Cover image. Match the orientation chosen above.")
    featured = models.BooleanField(default=False, help_text="Show on the home page.")
    date = models.DateField(default=timezone.localdate)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "media item"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("hub:media_detail", args=[self.pk])

    @property
    def is_portrait(self):
        return self.orientation == self.PORTRAIT

    @property
    def embed_url(self):
        """An iframe-able URL for YouTube and Vimeo links; None for platforms that block embedding."""
        u = self.video_url
        m = re.search(r"(?:youtube\.com/(?:watch\?(?:.*&)?v=|shorts/|embed/)|youtu\.be/)([\w-]{11})", u)
        if m:
            return f"https://www.youtube-nocookie.com/embed/{m.group(1)}"
        m = re.search(r"vimeo\.com/(?:video/)?(\d+)", u)
        if m:
            return f"https://player.vimeo.com/video/{m.group(1)}"
        return None


# --------------------------------------------------------------------------- portfolio
class Project(models.Model):
    title = models.CharField(max_length=160)
    client = models.CharField(max_length=120, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to="projects/", blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma separated")
    link = models.URLField(blank=True, help_text="Case study, demo or repository.")
    year = models.PositiveIntegerField(default=timezone.now().year)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-year"]

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return split_tags(self.tags)


# --------------------------------------------------------------------------- about
class CoreValue(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="team/", blank=True)
    linkedin_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    @property
    def initials(self):
        return "".join(p[0] for p in self.name.split()[:2]).upper()


class AboutSection(models.Model):
    """Free-form extra blocks on the About page (impact, partners, approach...)."""

    title = models.CharField(max_length=120)
    body = models.TextField(help_text="Blank lines start a new paragraph.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "other about-page section"

    def __str__(self):
        return self.title

    @property
    def paragraphs(self):
        return [p.strip() for p in self.body.split("\n\n") if p.strip()]


# --------------------------------------------------------------------------- newsletter
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    wants_membership = models.BooleanField("Interested in membership", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
