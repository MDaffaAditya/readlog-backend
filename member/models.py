from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username
    
    def __str__(self):
        return self.username
    
    class Meta:
        ordering = ['-date_joined']


class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        help_text="Link to User account"
    )
    
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True,
        help_text="Profile picture (recommended: 400x400px)"
    )
    
    bio = models.TextField(
        max_length=500, 
        blank=True,
        help_text="User biography (max 500 characters)"
    )
    
    # Social Links - Store username only
    twitter_username = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Twitter username (without @)"
    )
    
    instagram_username = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Instagram username (without @)"
    )
    
    website_url = models.URLField(
        max_length=200, 
        blank=True,
        help_text="Personal website URL (full URL with https://)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def twitter_url(self):
        if self.twitter_username:
            # Remove @ if user included it
            username = self.twitter_username.lstrip('@')
            return f"https://twitter.com/{username}"
        return None
    
    @property
    def instagram_url(self):
        if self.instagram_username:
            # Remove @ if user included it
            username = self.instagram_username.lstrip('@')
            return f"https://instagram.com/{username}"
        return None
    
    @property
    def has_social_links(self):
        """Check if user has any social links"""
        return bool(self.twitter_username or self.instagram_username or self.website_url)


# SIGNALS - Auto-create Profile ketika user dibuat
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
