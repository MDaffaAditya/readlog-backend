from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from contents.models import Comic, Novel


class UserLibrary(models.Model):
    STATUS_CHOICES = [
        ("plan_to_read", "Plan to Read"),
        ("reading", "Reading"),
        ("completed", "Completed"),
        ("on_hold", "On Hold"),
        ("dropped", "Dropped"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, null=True, blank=True)
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="plan_to_read"
    )
    progress = models.PositiveIntegerField(default=0)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comic"],
                condition=models.Q(comic__isnull=False),
                name="unique_user_comic_library",
            ),
            models.UniqueConstraint(
                fields=["user", "novel"],
                condition=models.Q(novel__isnull=False),
                name="unique_user_novel_library",
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'updated_at']),
        ]

    # VALIDATION
    def clean(self):
        """Validasi data integrity"""
        if not self.comic and not self.novel:
            raise ValidationError("Must have comic or novel.")

        if self.comic and self.novel:
            raise ValidationError("Cannot have both comic and novel.")

        # Validasi progress tidak melebihi total chapters
        total = self.total_chapters
        if total > 0 and self.progress > total:
            raise ValidationError(
                f"Progress ({self.progress}) cannot exceed total chapters ({total})."
            )

    # SAVE LOGIC
    def save(self, *args, **kwargs):
        # Track perubahan status
        old_status = None
        if self.pk:
            try:
                old_instance = UserLibrary.objects.get(pk=self.pk)
                old_status = old_instance.status
            except UserLibrary.DoesNotExist:
                pass

        # Set started_at hanya pertama kali mulai baca
        if self.status in ["reading", "on_hold"] and not self.started_at:
            self.started_at = timezone.now()

        # Manage completed_at timestamp
        if self.status == "completed":
            if old_status != "completed" and not self.completed_at:
                self.completed_at = timezone.now()
        else:
            if old_status == "completed":
                self.completed_at = None

        # Auto-cap progress jika melebihi total (untuk safety)
        # User tetap bisa set completed tanpa progress penuh
        total = self.total_chapters
        if total > 0 and self.progress > total:
            self.progress = total

        # Validasi dasar
        self.full_clean()
        super().save(*args, **kwargs)

    # HELPERS
    def get_target(self):
        return self.comic or self.novel

    @property
    def total_chapters(self):
        target = self.get_target()
        return target.total_chapters if target else 0

    @property
    def completion_percentage(self):
        if self.total_chapters == 0:
            return 0
        return round((self.progress / self.total_chapters) * 100, 2)

    @property
    def is_caught_up(self):
        """Check if user sudah baca semua chapter yang tersedia"""
        return self.progress >= self.total_chapters if self.total_chapters > 0 else False

    def __str__(self):
        return f"{self.user.username} - {self.get_target()} ({self.status})"