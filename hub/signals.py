from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Product, Notification, Watch
@receiver(pre_save, sender=Product)
def old_price(sender, instance, **kwargs):
    instance._old_price = Product.objects.filter(pk=instance.pk).values_list('price', flat=True).first() if instance.pk else None
@receiver(post_save, sender=Product)
def notify_price(sender, instance, created, **kwargs):
    old = getattr(instance, '_old_price', None)
    if old is not None and instance.price < old and instance.discount:
        Notification.objects.bulk_create([Notification(user_id=w.user_id, title=f'{instance.name} is now ${instance.price} at {instance.store} — {instance.discount}% off.') for w in Watch.objects.filter(product=instance)])

from .models import ServiceAlert, AlertPreference
@receiver(post_save, sender=ServiceAlert)
def notify_service(sender, instance, created, **kwargs):
    if not created or not instance.active: return
    preferences = AlertPreference.objects.filter(city=instance.city)
    if instance.kind not in ('weather', 'transport'): return
    preferences = preferences.filter(**{instance.kind: True})
    Notification.objects.bulk_create([Notification(user_id=p.user_id, title=f'{instance.city.title()} {instance.kind}: {instance.title} — {instance.description}'[:240]) for p in preferences])
