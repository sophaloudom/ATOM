from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from .models import Product, Watch, Notification
class WorkflowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('tester',email='test@example.com',password='safe-demo-pass-123')
        self.product = Product.objects.create(name='Milk',store='Test store',category='Dairy',unit='2L',price=5,regular_price=6)
    @patch('hub.views.weather',return_value={'temperature':19,'wind':10,'live':False})
    def test_dashboard_and_search(self,_):
        self.assertContains(self.client.get('/'), 'Milk')
        self.assertNotContains(self.client.get('/?q=bread'), '<h3>Milk</h3>')
        self.assertContains(self.client.get('/?city=wellington'),'Wellington, NZ')
    def test_watch_and_price_drop(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(f'/watch/{self.product.pk}/').status_code,302)
        self.assertTrue(Watch.objects.filter(user=self.user,product=self.product).exists())
        Notification.objects.all().delete()
        self.product.price=Decimal('4'); self.product.save()
        self.assertEqual(Notification.objects.count(),1)
        self.product.save()
        self.assertEqual(Notification.objects.count(),1)
        self.client.post('/notifications/read/')
        self.assertTrue(Notification.objects.get().read)
    def test_auth_and_post_required(self):
        self.assertEqual(self.client.post(f'/watch/{self.product.pk}/').status_code,302)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(f'/watch/{self.product.pk}/').status_code,405)
    def test_seed_repeatable(self):
        call_command('seed_demo'); counts=Product.objects.count()
        call_command('seed_demo'); self.assertEqual(counts,Product.objects.count())
    def test_email_delivery(self):
        Notification.objects.create(user=self.user,title='Milk price dropped')
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            call_command('send_alerts')
            from django.core import mail
            self.assertEqual(len(mail.outbox),1)
            call_command('send_alerts'); self.assertEqual(len(mail.outbox),1)
    def test_signup_email(self):
        response=self.client.post('/signup/',{'username':'newuser','email':'new@example.com','password1':'ComplexPass-9293','password2':'ComplexPass-9293'})
        self.assertEqual(response.status_code,302)
        self.assertEqual(get_user_model().objects.get(username='newuser').email,'new@example.com')

    def test_city_alert_subscriptions(self):
        from .models import AlertPreference, ServiceAlert
        AlertPreference.objects.create(user=self.user,city='wellington')
        ServiceAlert.objects.create(city='auckland',kind='transport',title='Auckland test',description='Notice')
        self.assertEqual(Notification.objects.count(),0)
        notice=ServiceAlert.objects.create(city='wellington',kind='transport',title='Wellington test',description='Notice')
        self.assertEqual(Notification.objects.count(),1)
        notice.save(); self.assertEqual(Notification.objects.count(),1)
    @patch('hub.services.urlopen',side_effect=OSError('offline'))
    def test_weather_fallback_is_labeled(self,_):
        from django.core.cache import cache
        from .services import weather
        cache.clear()
        self.assertFalse(weather('wellington')['live'])
    @patch('hub.management.commands.check_weather.weather',return_value={'live':True,'warning':True,'wind':65})
    def test_weather_alert_deduplication(self,_):
        from .models import AlertPreference
        AlertPreference.objects.create(user=self.user,city='auckland')
        call_command('check_weather'); call_command('check_weather')
        self.assertEqual(Notification.objects.count(),1)
    def test_health_database_available(self):
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    @patch('django.db.connection.cursor', side_effect=Exception('database unavailable'))
    def test_health_database_unavailable(self, _):
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {'status': 'unavailable'})
