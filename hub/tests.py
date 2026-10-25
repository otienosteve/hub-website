from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from .models import Course, CourseApplication, CourseOutcome


@override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class CourseApplicationTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Agent Engineering",
            summary="Build useful AI agents.",
            duration_days=5,
            price="15000.00",
            payment_url="https://payments.example.test/agent-engineering",
        )

    def application_data(self, **overrides):
        data = {
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
            "phone_number": "+254700000000",
            "county": "Nairobi",
            "current_occupation": "Engineer",
            "institution_company": "Analytical Engines Ltd",
            "python_proficiency": "intermediate",
        }
        data.update(overrides)
        return data

    def test_course_detail_shows_price_outcomes_and_apply_button(self):
        CourseOutcome.objects.create(course=self.course, title="Build and deploy agents")

        response = self.client.get(self.course.get_absolute_url())

        self.assertContains(response, "KSh 15,000.00")
        self.assertContains(response, "Course outcomes")
        self.assertContains(response, "Build and deploy agents")
        self.assertContains(response, "Apply now")

    def test_application_is_saved_and_redirects_to_configured_payment_page(self):
        response = self.client.post(
            reverse("hub:apply_course", args=[self.course.slug]),
            self.application_data(),
        )

        self.assertRedirects(response, self.course.payment_url, fetch_redirect_response=False)
        application = CourseApplication.objects.get()
        self.assertEqual(application.course, self.course)
        self.assertEqual(application.email, "ada@example.com")
        self.assertEqual(application.python_proficiency, "intermediate")

    def test_application_requires_a_configured_payment_page(self):
        self.course.payment_url = ""
        self.course.save()

        response = self.client.post(
            reverse("hub:apply_course", args=[self.course.slug]),
            self.application_data(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "payment page is not configured")
        self.assertContains(response, "data-open-on-load")
        self.assertEqual(CourseApplication.objects.count(), 0)

    def test_invalid_application_is_not_saved_and_form_reopens(self):
        response = self.client.post(
            reverse("hub:apply_course", args=[self.course.slug]),
            self.application_data(email="not-an-email", python_proficiency="advanced"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-open-on-load")
        self.assertContains(response, "Enter a valid email address")
        self.assertEqual(CourseApplication.objects.count(), 0)
