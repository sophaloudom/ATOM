import time
from django.core.management import call_command
from django.core.management.base import BaseCommand
class Command(BaseCommand):
    help = 'Single development worker: check weather and send pending email every 10 minutes.'
    def handle(self,*args,**kwargs):
        while True:
            try:
                call_command('check_weather')
                call_command('send_alerts')
            except Exception as error:
                self.stderr.write(f'Alert cycle failed ({type(error).__name__}); retrying next cycle.')
            time.sleep(600)
