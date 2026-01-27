from rest_framework import serializers
from member.models import User, Profile


class UserPublicSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'date_joined']
        read_only_fields = ['id', 'username', 'full_name', 'date_joined']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    # Social URLs (computed from usernames)
    twitter_url = serializers.URLField(read_only=True)
    instagram_url = serializers.URLField(read_only=True)
    has_social_links = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'username',
            'full_name',
            'avatar',
            'bio',
            'twitter_username',
            'twitter_url',
            'instagram_username',
            'instagram_url',
            'website_url',
            'has_social_links',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 
            'user', 
            'username', 
            'full_name',
            'twitter_url',
            'instagram_url',
            'has_social_links',
            'created_at', 
            'updated_at'
        ]
    
    def get_instagram_url(self, obj):
        if obj.instagram_username:
            return f"https://instagram.com/{obj.instagram_username}"
        return None

    # Mengecek apakah ada link sosial yang aktif
    def get_has_social_links(self, obj):
        return any([obj.twitter_username, obj.instagram_username, obj.website_url])
    
    # VALIDASI: Membersihkan input @ agar database tetap bersih
    def validate_twitter_username(self, value):
        return value.lstrip('@') if value else value
    
    def validate_instagram_username(self, value):
        return value.lstrip('@') if value else value