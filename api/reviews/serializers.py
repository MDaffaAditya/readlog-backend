from rest_framework import serializers
from reviews.models import Review
from api.contents.serializers import ComicSerializer, NovelSerializer

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    comic_detail = ComicSerializer(source="comic", read_only=True)
    novel_detail = NovelSerializer(source="novel", read_only=True)
    
    user_avatar = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "username", "user_id", 'user_avatar', "content", "rating", "created_at",
            "comic", "comic_detail", "novel", "novel_detail",
            "likes_count", "is_liked"
        ]
        read_only_fields = ["user", "created_at", "likes_count", "is_liked"]

    def get_user_avatar(self, obj):
        profile = getattr(obj.user, 'profile', None)
        
        if profile and profile.avatar:
            return self.context['request'].build_absolute_uri(profile.avatar.url)
        return None

    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def validate(self, data):
        comic = data.get("comic") or getattr(self.instance, "comic", None)
        novel = data.get("novel") or getattr(self.instance, "novel", None)

        if not comic and not novel:
            raise serializers.ValidationError(
                "Review must be linked to either a Comic or a Novel."
            )
        if comic and novel:
            raise serializers.ValidationError(
                "Review cannot be linked to both Comic and Novel at the same time."
            )
        return data

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        review = Review.objects.create(**validated_data)
        if review.comic:
            review.comic.update_average_rating()
        if review.novel:
            review.novel.update_average_rating()
        return review
