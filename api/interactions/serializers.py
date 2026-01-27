from rest_framework import serializers
from interactions.models import Favorite, Like
from api.contents.serializers import ComicSerializer, NovelSerializer

class FavoriteSerializer(serializers.ModelSerializer):
    target_type = serializers.SerializerMethodField(read_only=True)
    target_id = serializers.SerializerMethodField(read_only=True)
    target_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "user", "comic", "novel", "rank", "created_at", "target_type", "target_id", "target_detail"]
        read_only_fields = ["created_at", "user", "rank"]

    def get_target_type(self, obj):
        return "comic" if obj.comic else "novel"

    def get_target_id(self, obj):
        return obj.comic_id or obj.novel_id
    
    def get_target_detail(self, obj):
        # Mengambil objek request dari context serializer
        request = self.context.get('request')
        
        target = obj.comic if obj.comic else obj.novel
        if not target:
            return None

        # Mengambil URL asli
        image_url = target.cover_image.url if target.cover_image else None
        
        # Jika ada request, Django akan mengubah path relatif menjadi URL absolut otomatis
        if image_url and request is not None:
            image_url = request.build_absolute_uri(image_url)

        # Menentukan type-specific fields
        extra_info = {
            "comic_type": target.comic_type if obj.comic else None,
            "novel_type": target.novel_type if obj.novel else None,
        }

        return {
            "id": target.id,
            "title": target.title,
            "author": target.author,
            "cover_image": image_url, # Sekarang isinya URL lengkap
            "average_rating": float(target.average_rating),
            "status": target.status,
            **{k: v for k, v in extra_info.items() if v is not None}
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FavoriteReorderSerializer(serializers.Serializer):
    favorites = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        allow_empty=False
    )

    def validate_favorites(self, value):
        user = self.context['request'].user
        for item in value:
            if 'id' not in item or 'rank' not in item:
                raise serializers.ValidationError("Each item must have 'id' and 'rank' fields.")
        favorite_ids = [item['id'] for item in value]
        user_favorites = Favorite.objects.filter(id__in=favorite_ids, user=user)
        if user_favorites.count() != len(favorite_ids):
            raise serializers.ValidationError("Some favorites don't belong to you or don't exist.")
        ranks = [item['rank'] for item in value]
        if len(ranks) != len(set(ranks)):
            raise serializers.ValidationError("Ranks must be unique.")
        return value


class LikeSerializer(serializers.ModelSerializer):
    review_detail = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Like
        fields = ["id", "user", "review", "created_at", "review_detail"]
        read_only_fields = ["user", "created_at"]

    def get_review_detail(self, obj):
        review = obj.review
        return {
            "id": review.id,
            "content": review.content[:100]+"..." if len(review.content)>100 else review.content,
            "rating": float(review.rating),
            "user": review.user.username,
            "likes_count": review.likes.count(),
            "created_at": review.created_at
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class LikeToggleSerializer(serializers.Serializer):
    review = serializers.IntegerField()

    def validate_review(self, value):
        from reviews.models import Review
        if not Review.objects.filter(id=value).exists():
            raise serializers.ValidationError("Review not found.")
        return value
