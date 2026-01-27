from django.db import migrations

def create_profiles_for_existing_users(apps, schema_editor):
    User = apps.get_model('member', 'User')
    Profile = apps.get_model('member', 'Profile')
    
    # Get users without profile
    users_without_profile = User.objects.filter(profile__isnull=True)
    
    profiles_to_create = []
    for user in users_without_profile:
        profiles_to_create.append(Profile(user=user))
    
    # Bulk create
    if profiles_to_create:
        Profile.objects.bulk_create(profiles_to_create)
        print(f"✓ Created {len(profiles_to_create)} profiles for existing users")
    else:
        print("✓ All users already have profiles")


def delete_all_profiles(apps, schema_editor):
    Profile = apps.get_model('member', 'Profile')
    Profile.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0002_alter_user_options_profile'), 
    ]

    operations = [
        migrations.RunPython(
            create_profiles_for_existing_users,
            reverse_code=delete_all_profiles
        ),
    ]