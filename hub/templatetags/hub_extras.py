from django import template

register = template.Library()


@register.filter
def tone(obj):
    """Pick one of four placeholder colour treatments from an object's id (used when no image is uploaded)."""
    return (getattr(obj, "pk", None) or 0) % 4 + 1
