from allauth.socialaccount.signals import pre_social_login
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Auto-create username if it's empty
@receiver(pre_social_login)
def create_username_if_empty(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    if not user.username:
        # Use email as the username or any other logic you prefer
        user.username = user.email.split('@')[0]
        user.save()
