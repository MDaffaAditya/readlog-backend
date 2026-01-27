from django.db import models


# GENRE MODEL
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# COMIC MODEL
class Comic(models.Model):
    TYPE_CHOICES = [
        ("manga", "Manga"),
        ("manhwa", "Manhwa"),
        ("manhua", "Manhua"),
        ("webtoon", "Webtoon"),
        ("comic", "Comic"),
    ]

    STATUS_CHOICES = [
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("hiatus", "Hiatus"),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    comic_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    genres = models.ManyToManyField(Genre, blank=True)
    release_year = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ongoing")
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="covers/comics", blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    total_chapters = models.PositiveIntegerField(default=0)
    total_volumes = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def update_average_rating(self):
        reviews = self.review_set.all()
        if reviews.exists():
            avg = sum([r.rating for r in reviews]) / reviews.count()
            self.average_rating = round(avg, 1)
        else:
            self.average_rating = 0.0
        self.save(update_fields=["average_rating"])

    def __str__(self):
        return f"{self.title} ({self.comic_type})"


# NOVEL MODEL
class Novel(models.Model):
    TYPE_CHOICES = [
        ("light novel", "Light Novel"),
        ("web novel", "Web Novel"),
        ("novel", "Novel"),
    ]

    STATUS_CHOICES = [
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("hiatus", "Hiatus"),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    novel_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    genres = models.ManyToManyField(Genre, blank=True)
    release_year = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ongoing")
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="covers/novels", blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    total_chapters = models.PositiveIntegerField(default=0)
    total_volumes = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def update_average_rating(self):
        reviews = self.review_set.all()
        if reviews.exists():
            avg = sum([r.rating for r in reviews]) / reviews.count()
            self.average_rating = round(avg, 1)
        else:
            self.average_rating = 0.0
        self.save(update_fields=["average_rating"])

    def __str__(self):
        return f"{self.title} ({self.novel_type})"


