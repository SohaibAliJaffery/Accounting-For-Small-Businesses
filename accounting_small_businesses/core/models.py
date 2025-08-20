from django.db import models
from django.conf import settings


class Organization(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.code} - {self.name}"


class Role(models.Model):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    CLERK = "clerk"
    VIEWER = "viewer"
    CHOICES = [
        (ADMIN, "Admin"),
        (ACCOUNTANT, "Accountant"),
        (CLERK, "Clerk"),
        (VIEWER, "Viewer"),
    ]
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, choices=CHOICES)

    class Meta:
        unique_together = [("org", "name")]


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)


class Attachment(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to="attachments/%Y/%m/%d")
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    ref = models.CharField(max_length=64, blank=True, default="")

    @classmethod
    def log(cls, org, user, action, **kwargs):
        return cls.objects.create(org=org, user=user, action=action, after=kwargs)
from django.db import models

# Create your models here.
