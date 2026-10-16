from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from hub.models import Notification
class Command(BaseCommand):
    help = 'Send pending price alerts. Schedule periodically; console email is the development default.'
    def handle(self,*args,**kwargs):
        count=0
        for notice in Notification.objects.filter(emailed=False).select_related('user'):
            if not notice.user.email: continue
            send_mail('ATOM · Price drop',notice.title,settings.DEFAULT_FROM_EMAIL,[notice.user.email],fail_silently=False)
            notice.emailed=True; notice.save(update_fields=['emailed']); count+=1
        self.stdout.write(f'Sent {count} alerts.')
