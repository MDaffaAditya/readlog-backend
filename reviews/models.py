from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from contents.models import Comic, Novel
from django.db.models import Q


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, null=True, blank=True)
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comic"],
                condition=Q(comic__isnull=False),
                name="unique_user_comic_review",
            ),
            models.UniqueConstraint(
                fields=["user", "novel"],
                condition=Q(novel__isnull=False),
                name="unique_user_novel_review",
            ),
        ]

    def clean(self):
        if not self.comic and not self.novel:
            raise ValidationError("Review must be linked to either a Comic or a Novel.")

        if self.comic and self.novel:
            raise ValidationError(
                "Review must not be linked to both Comic and Novel at the same time."
            )

    def __str__(self):
        target = self.comic or self.novel
        return f"Review by {self.user.username} on {target}"
