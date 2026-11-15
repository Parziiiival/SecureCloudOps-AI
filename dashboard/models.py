from django.db import models  # type: ignore[reportMissingModuleSource]

class SecurityFinding(models.Model):
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    title = models.CharField(max_length=255)
    tool = models.CharField(max_length=50, help_text="e.g., Trivy, Checkov, Bandit")
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    component = models.CharField(max_length=255, help_text="Affected file, package, or resource")
    status = models.CharField(max_length=50, default="Open")
    description = models.TextField(blank=True)
    remediation = models.TextField(blank=True, help_text="AI-generated or standard fix")
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.severity}] {self.title} ({self.tool})"