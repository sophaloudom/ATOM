from django.core.management.base import BaseCommand
from hub.models import Product, Departure, ServiceAlert
class Command(BaseCommand):
    help = 'Create clearly labeled demonstration inventory and transport data.'
    def handle(self, *args, **options):
        rows = [('Hass avocados','FreshChoice','Fruit & veg','🥑','each',1.49,2.50),('Fresh strawberries','New World','Fruit & veg','🍓','250g punnet',3.99,5.99),('Free range eggs','Woolworths','Dairy & eggs','🥚','6 pack',5.50,7.20),('Organic bananas','PAK’nSAVE','Fruit & veg','🍌','per kg',2.99,3.99),('Sourdough loaf','New World','Bakery','🍞','700g loaf',4.50,6),('Blue milk','Woolworths','Dairy & eggs','🥛','2 litres',3.85,4.80),('Atlantic salmon','FreshChoice','Meat & seafood','🐟','per 200g',8.99,12.99),('Broccoli','PAK’nSAVE','Fruit & veg','🥦','each',1.79,2.99)]
        for name,store,category,emoji,unit,price,regular in rows:
            Product.objects.get_or_create(name=name,store=store,defaults=dict(category=category,emoji=emoji,unit=unit,price=price,regular_price=regular))
        for route,destination,mode,minutes,status in [('NX1','Albany via Northern Busway','Bus',3,'On time'),('70','Botany via Panmure','Bus',8,'On time'),('WEST','Swanson','Train',12,'5 min delay'),('DEV','Devonport','Ferry',18,'On time')]:
            Departure.objects.get_or_create(route=route,defaults=dict(destination=destination,mode=mode,minutes=minutes,status=status))
        ServiceAlert.objects.get_or_create(title='Western Line service changes',defaults=dict(kind='transport',description='Demo notice: allow extra travel time. Check your operator before travelling.'))
        for route,destination,mode,minutes in [('1','Island Bay','Bus',4),('2','Karori','Bus',9),('JVL','Johnsonville','Train',14),('HVL','Upper Hutt','Train',22)]:
            Departure.objects.get_or_create(route=route,city='wellington',defaults=dict(destination=destination,mode=mode,minutes=minutes))
        ServiceAlert.objects.get_or_create(title='Wellington waterfront bus diversion',city='wellington',defaults=dict(kind='transport',description='Demo notice: some stops may change. Check Metlink for current updates.'))
        self.stdout.write(self.style.SUCCESS('Demo data ready (not live retailer or transport data).'))
