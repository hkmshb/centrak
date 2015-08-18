from django.test import TestCase

from enumeration.models import Manufacturer, MobileOS



class DeviceOptionViewTest(TestCase):
    
    def test_manufactuers_listing(self):
        create_test_manufacturers()
        
        response = self.client.get('/enum/device-options/manufacturers/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(5, len(response.context['manufacturer_list']))    
    
    def test_saving_a_POST_request(self):
        manufacturer = {'name': 'Samsung'}
        url = '/enum/device-options/manufacturers/'
        response = self.client.post(url, data=manufacturer)
        self.assertEqual(302, response.status_code)
        
        items = Manufacturer.objects.all()
        self.assertEqual(1, len(items))
    
    

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
    