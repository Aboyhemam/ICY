from allauth.socialaccount.signals import pre_social_login
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount

@receiver(pre_social_login)
def create_or_link_user(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    email = user.email

    # Check if the user already exists
    existing_user = User.objects.filter(email=email).first()

    if existing_user:
        # If a user with the same email exists, link the social account to the existing user
        socialaccount = SocialAccount.objects.filter(user=existing_user, provider='google').first()
        
        if socialaccount is None:
            # Link the Google social account to the existing user
            sociallogin.connect(request, existing_user)
    else:
        # If no existing user, proceed as normal and create a new user
        if not user.username:
            # Auto-create username based on the email (if not already set)
            user.username = email.split('@')[0]
        user.save()
