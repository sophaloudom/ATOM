from django.core.management.base import BaseCommand
from django.utils import timezone
from hub.services import weather
from hub.models import ServiceAlert
class Command(BaseCommand):
    help = 'Check both cities for high winds; create one advisory per city per day. Schedule every 10 minutes.'
    def handle(self,*args,**kwargs):
        for city in ('auckland','wellington'):
            data=weather(city)
            if not data['live']:
                self.stderr.write(f'{city}: provider unavailable; no alert generated from demo data.')
                continue
            if data['warning']:
                ServiceAlert.objects.get_or_create(city=city,kind='weather',title=f'Strong wind advisory · {timezone.localdate()}', defaults={'description':f"Wind speed {data['wind']} km/h. Take care outdoors. This is an ATOM advisory, not an official warning."})
            self.stdout.write(f'{city}: checked live conditions')
