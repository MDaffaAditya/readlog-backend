from rest_framework import serializers
from library.models import UserLibrary
from api.contents.serializers import ComicSerializer, NovelSerializer

class UserLibrarySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    comic_detail = ComicSerializer(source="comic", read_only=True)
    novel_detail = NovelSerializer(source="novel", read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Property dari model
    total_chapters = serializers.IntegerField(read_only=True)
    completion_percentage = serializers.FloatField(read_only=True)
    is_caught_up = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserLibrary
        fields = [
            "id", "user", "username", "comic", "comic_detail", "novel", "novel_detail",
            "status", "status_display", "progress", "total_chapters", "completion_percentage",
            "is_caught_up", "started_at", "completed_at", "created_at", "updated_at"
        ]
        read_only_fields = [
            "user", "total_chapters", "completion_percentage", "is_caught_up",
            "started_at", "completed_at", "created_at", "updated_at"
        ]

    def validate(self, data):
        # Saat update (PATCH/PUT), ambil instance yang sudah ada
        if self.instance:
            comic = data.get("comic") or self.instance.comic
            novel = data.get("novel") or self.instance.novel
            progress = data.get("progress", self.instance.progress)
        else:
            # Saat create (POST), ambil dari data yang dikirim
            comic = data.get("comic")
            novel = data.get("novel")
            progress = data.get("progress", 0)

        # Validasi: harus ada salah satu
        if not comic and not novel:
            raise serializers.ValidationError("Library entry must be linked to either a Comic or a Novel.")
        
        # Validasi: tidak boleh keduanya
        if comic and novel:
            raise serializers.ValidationError("Library entry cannot be linked to both Comic and Novel at the same time.")

        # Validasi progress tidak melebihi total chapters
        if progress is not None:
            total_chapters = 0
            if comic:
                total_chapters = comic.total_chapters
            elif novel:
                total_chapters = novel.total_chapters
            
            if total_chapters > 0 and progress > total_chapters:
                raise serializers.ValidationError({
                    "progress": f"Progress cannot exceed total chapters ({total_chapters})."
                })

        return data

    def create(self, validated_data):
        # User sudah di-set dari perform_create di viewset
        # Tapi keep ini untuk safety jika dipanggil langsung
        if "user" not in validated_data:
            validated_data["user"] = self.context["request"].user
        return super().create(validated_data)