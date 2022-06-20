from django.db.models.signals import post_save
from django.dispatch import receiver
from django_otp.plugins.otp_totp.models import TOTPDevice

from .models import User, Balance, Document


@receiver(post_save, sender=User)
def create_balance_for_user(instance: User, created, **kwargs):
    if created:
        Balance.objects.create(user=instance)


@receiver(post_save, sender=Document)
def set_verified_true(instance: Document, **kwargs):
    if instance.status == instance.Status.ACCEPTED:
        instance.user.verified = True
        instance.user.save(update_fields=['verified'])
