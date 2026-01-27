from rest_framework import serializers
from contents.models import Genre, Comic, Novel


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class ComicSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, write_only=True, source="genres"
    )
    media_type = serializers.SerializerMethodField()
    reviews_count = serializers.IntegerField(source='review_set.count', read_only=True)

    class Meta:
        model = Comic
        fields = [
            "id",
            "title",
            "author",
            "comic_type",
            "genres",
            "genre_ids",
            "release_year",
            "status",
            "description",
            "cover_image",
            "average_rating",
            "reviews_count",
            "total_chapters",
            "total_volumes",
            "updated_at",
            "media_type",
        ]
        read_only_fields = ["average_rating", "reviews_count", "updated_at"]

    def get_media_type(self, obj):
        return "comic"


class NovelSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, write_only=True, source="genres"
    )
    media_type = serializers.SerializerMethodField()
    reviews_count = serializers.IntegerField(source='review_set.count', read_only=True)

    class Meta:
        model = Novel
        fields = [
            "id",
            "title",
            "author",
            "novel_type",
            "genres",
            "genre_ids",
            "release_year",
            "status",
            "description",
            "cover_image",
            "average_rating",
            "reviews_count",
            "total_chapters",
            "total_volumes",
            "updated_at",
            "media_type",
        ]
        read_only_fields = ["average_rating", "reviews_count", "updated_at"]

    def get_media_type(self, obj):
        return "novel"