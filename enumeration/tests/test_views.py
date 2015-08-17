from django.test import TestCase

from enumeration.models import Manufacturer, MobileOS



class DeviceOptionViewTest(TestCase):
    
    def test_lists_manufacturers_and_mobile_oses(self):
        create_test_manufacturers()
        create_test_mobile_oses()
        
        response = self.client.get('/enum/device-options/')
        self.assertEqual(200, response.status_code)
        
        context = response.context
        self.assertEqual(5, len(context['manufacturer_list']))
        self.assertEqual(5, len(context['mobile_os_list']))


def create_test_manufacturers():
    Manufacturer.objects.create(name='Apple')
    Manufacturer.objects.create(name='BlackBerry')
    Manufacturer.objects.create(name='LG')
    Manufacturer.objects.create(name='Samsung')
    Manufacturer.objects.create(name='Sony')


def create_test_mobile_oses():
    MobileOS.objects.create(name='Android')
    MobileOS.objects.create(name='BlackBerry')
    MobileOS.objects.create(name='iOS')
    MobileOS.objects.create(name='Windows Phone')
    MobileOS.objects.create(name='Tizen')
    