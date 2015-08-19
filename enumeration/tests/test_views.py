from django.test import TestCase

from enumeration.models import Manufacturer, MobileOS
from enumeration.forms import UNIQUE_MANUFACTURER_NAME_ERROR


class DeviceOptionViewTest(TestCase):
    url_manufacturers = '/enum/device-options/manufacturers/'
    url_manufacturer_edit = '/enum/device-options/manufacturers/update'
    
    def test_manufactuers_listing(self):
        create_test_manufacturers()
        
        response = self.client.get(self.url_manufacturers)
        self.assertEqual(200, response.status_code)
        self.assertEqual(5, len(response.context['manufacturer_list']))    
    
    def test_saving_a_POST_request(self):
        data = {'name': 'Samsung'}
        response = self.client.post(self.url_manufacturers, data=data)
        self.assertEqual(302, response.status_code)
        
        items = Manufacturer.objects.all()
        self.assertEqual(1, len(items))
    
    def test_displays_notification_on_successful_save(self):
        data = {'name': 'Samsung'}
        response = self.client.post(self.url_manufacturers, data=data)
        self.assertEqual(302, response.status_code)
        
        response = self.client.get(self.url_manufacturers)
        self.assertContains(response, 'Manufacturer added successfully.')
    
    def test_displays_blank_name_validation_error(self):
        response = self.client.post(self.url_manufacturers, data={'name':''})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'This field is required')

    def test_displays_non_unique_name_validation_error(self):
        Manufacturer.objects.create(name='Samsung')
        data = {'name': 'Samsung'}
        
        response = self.client.post(self.url_manufacturers, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, UNIQUE_MANUFACTURER_NAME_ERROR)

    def test_updating_via_POST_request(self):
        manufacturer = Manufacturer.objects.create(name='Samsung')
        self.assertEqual(1, len(Manufacturer.objects.all()))
        
        data = {'id': manufacturer.id, 'name': 'Lenovo'}
        response = self.client.post(self.url_manufacturer_edit, data=data)
    
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, 'Samsung')
        self.assertContains(response, 'Lenovo')
    
    def test_displays_error_when_updating_non_existing_record(self):
        self.fail('write test')


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
    