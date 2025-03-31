from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PaymentRequest

@receiver(post_save, sender=PaymentRequest)
def create_payment_request_notification(sender, instance, created, **kwargs):
    if created:
        PaymentRequest.objects.create(
            receiver=instance.receiver,
            sender=instance.sender,
            amount=instance.amount,
            timestamp=instance.timestamp,
            is_read=False,
        )
