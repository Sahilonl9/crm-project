import uuid

from django.conf import settings
from django.db import models


class Lead(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("interested", "Interested"),
        ("closed", "Closed"),
    ]

    SOURCE_CHOICES = [
        ("website", "Website"),
        ("referral", "Referral"),
        ("social_media", "Social Media"),
        ("cold_call", "Cold Call"),
        ("email", "Email Campaign"),
        ("event", "Event"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_leads",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_leads",
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="other")
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    follow_up_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "leads"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"


class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="lead_notes",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lead_notes"
        ordering = ["-created_at"]

    def __str__(self):
        author_name = self.author.full_name if self.author else "Unknown"
        return f"Note on {self.lead.name} by {author_name}"
