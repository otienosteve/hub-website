import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


class VisitNotificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            settings.VISIT_NOTIFICATION_EMAIL
            and request.method == "GET"
            and response.status_code == 200
            and response.get("Content-Type", "").startswith("text/html")
            and not request.path.startswith("/admin/")
        ):
            self._send_notification(request)
        return response

    @staticmethod
    def _send_notification(request):
        subject = "Website page visit"
        message = (
            f"A visitor loaded {request.path} on {request.get_host()} "
            f"at {timezone.localtime():%Y-%m-%d %H:%M:%S %Z}."
        )
        try:
            sent_count = send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.VISIT_NOTIFICATION_EMAIL],
                fail_silently=False,
            )
        except (OSError, SMTPException):
            logger.exception("Could not send website visit notification")
        else:
            if not sent_count:
                logger.error("Website visit notification email was not sent")
