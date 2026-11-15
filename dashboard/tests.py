from django.test import TestCase
from django.urls import reverse
from .models import SecurityFinding


class DashboardTests(TestCase):
    def test_dashboard_renders_findings(self):
        SecurityFinding.objects.create(
            title="Test CVE Vulnerability",
            tool="Trivy",
            severity="HIGH",
            component="requirements.txt",
        )
        response = self.client.get(reverse("dashboard_index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test CVE Vulnerability")