from django.contrib.auth import get_user_model
from django.db.models import signals
from django.dispatch import receiver

from core.models import UserProfile



User = get_user_model()


@receiver(signals.post_save, sender=User)
def on_user_created(sender, **kwargs):
    """
    Listens for superuser creation and creates an associated userprofile
    record in order to prevent having a user record without a matching
    userprofile record entry.
    """
    instance = kwargs.get('instance', None)
    if instance and instance.is_superuser:
        try:
            UserProfile.objects.create(user=instance)
            print("Superuser user-profile created successfully.")
        except Exception as ex:
            print("Unable to create Superuser user-profile.")
            print(str(ex))
