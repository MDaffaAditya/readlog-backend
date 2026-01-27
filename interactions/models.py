from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q, Max, F

class BaseInteraction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_set"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Favorite(BaseInteraction):
    comic = models.ForeignKey(
        "contents.Comic",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="favorites"
    )
    novel = models.ForeignKey(
        "contents.Novel",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="favorites"
    )
    rank = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["rank"]
        constraints = [
            # Unique per user per target
            models.UniqueConstraint(fields=["user", "comic"], condition=Q(comic__isnull=False), name="unique_user_comic_favorite"),
            models.UniqueConstraint(fields=["user", "novel"], condition=Q(novel__isnull=False), name="unique_user_novel_favorite"),
            # Unique rank per type
            models.UniqueConstraint(fields=["user", "rank", "comic"], condition=Q(comic__isnull=False), name="unique_comic_rank_per_user"),
            models.UniqueConstraint(fields=["user", "rank", "novel"], condition=Q(novel__isnull=False), name="unique_novel_rank_per_user"),
        ]

    def clean(self):
        if not self.comic and not self.novel:
            raise ValidationError("Favorite must target either a comic or a novel.")
        if self.comic and self.novel:
            raise ValidationError("Favorite cannot target both comic and novel.")
        if self.rank is not None and self.rank < 1:
            raise ValidationError("Rank must be >= 1.")

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            if self.comic:
                qs = Favorite.objects.select_for_update().filter(user=self.user, comic__isnull=False)
            elif self.novel:
                qs = Favorite.objects.select_for_update().filter(user=self.user, novel__isnull=False)
            else:
                raise ValidationError("Favorite must have a target")

            # Jika rank tidak diberikan, append terakhir
            if not self.pk and self.rank is None:
                max_rank = qs.aggregate(max=Max("rank"))["max"] or 0
                self.rank = max_rank + 1

            # Geser rank lain jika rank baru bentrok
            elif self.pk:
                old = Favorite.objects.select_for_update().get(pk=self.pk)
                if old.rank != self.rank:
                    if self.rank < old.rank:
                        # naikkan rank antara rank baru sampai rank lama
                        qs.filter(rank__gte=self.rank, rank__lt=old.rank).update(rank=F("rank") + 1)
                    elif self.rank > old.rank:
                        # turunkan rank antara rank lama sampai rank baru
                        qs.filter(rank__lte=self.rank, rank__gt=old.rank).update(rank=F("rank") - 1)
            else:
                # Untuk new object dengan rank diberikan, geser rank lain biarr tidak double
                qs.filter(rank__gte=self.rank).update(rank=F("rank") + 1)

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            if self.comic:
                qs = Favorite.objects.select_for_update().filter(user=self.user, comic__isnull=False, rank__gt=self.rank)
            elif self.novel:
                qs = Favorite.objects.select_for_update().filter(user=self.user, novel__isnull=False, rank__gt=self.rank)
            else:
                qs = Favorite.objects.none()
            # turunkan semua rank lebih besar 1
            qs.update(rank=F("rank") - 1)
            super().delete(*args, **kwargs)

    @property
    def target(self):
        return self.comic or self.novel

    def __str__(self):
        return f"{self.user.username} #{self.rank} → {self.target}"


# LIKE
class Like(BaseInteraction):
    review = models.ForeignKey(
        "reviews.Review",
        on_delete=models.CASCADE,
        related_name="likes"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "review"],
                name="unique_user_review_like"
            ),
        ]
        indexes = [
            models.Index(fields=["review", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    @classmethod
    def toggle(cls, user, review):
        try:
            like = cls.objects.get(user=user, review=review)
            like.delete()
            return None, False
        except cls.DoesNotExist:
            like = cls.objects.create(user=user, review=review)
            return like, True

    def __str__(self):
        return f"{self.user.username} liked review #{self.review_id}"
