from django.contrib.messages.api import get_messages
from django.http.response import Http404
from django.test import TestCase

from enumeration.models import Manufacturer, MobileOS
from enumeration.forms import UNIQUE_MANUFACTURER_NAME_ERROR

from core.utils import MSG_FMT_SUCCESS_ADD, MSG_FMT_SUCCESS_DELETE, \
    MSG_FMT_ERROR_DELETE, MSG_FMT_WARN_DELETE



class DeviceOptionViewTest(TestCase):
    url_manufacturers = '/enum/device-options/manufacturers/'
    url_manufacturer_update = '/enum/device-options/manufacturers/update'
    url_manufacturer_delete = '/enum/device-options/manufacturers/delete'
    
    def test_manufacturers_listing(self):
        self.create_test_manufacturers()
        
        response = self.client.get(self.url_manufacturers)
        self.assertEqual(200, response.status_code)
        self.assertEqual(5, len(response.context['record_list']))    
    
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
        self.assertContains(response, MSG_FMT_SUCCESS_ADD % 'Manufacturer')
    
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
    
    def test_deleting_single_item_via_POST_request(self):
        manufacturer = Manufacturer.objects.create(name='Samsung')
        data = {'record_ids': manufacturer.id }
        
        response = self.client.post(self.url_manufacturer_delete, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(0, len(Manufacturer.objects.all()))
        
        response = self.client.get(self.url_manufacturers)
        self.assertContains(response, MSG_FMT_SUCCESS_DELETE % 'manufacturer(s)')
        
    def test_deleting_multiple_items_via_POST_request(self):
        manufacturer1 = Manufacturer.objects.create(name='Samsung')
        manufacturer2 = Manufacturer.objects.create(name='Motorola')
        Manufacturer.objects.create(name='Apple')
        
        self.assertEqual(3, len(Manufacturer.objects.all()))
        
        data = {'record_ids': [manufacturer1.id, manufacturer2.id]}        
        response = self.client.post(self.url_manufacturer_delete, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, len(Manufacturer.objects.all()))
        
        response = self.client.get(self.url_manufacturers)
        self.assertContains(response, MSG_FMT_SUCCESS_DELETE % 'manufacturer(s)')
        
    def test_displays_warning_for_partial_items_deletion(self):
        manufacturer1 = Manufacturer.objects.create(name='Samsung')
        Manufacturer.objects.create(name='Motorola')
        
        self.assertEqual(2, len(Manufacturer.objects.all()))
        
        data = {'record_ids': [manufacturer1.id, 201508]}        
        response = self.client.post(self.url_manufacturer_delete, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, len(Manufacturer.objects.all()))
        
        response = self.client.get(self.url_manufacturers)
        self.assertContains(response, MSG_FMT_WARN_DELETE % ('manufacturer(s)', 1))
    
    def test_displays_error_for_no_item_deletion(self):
        Manufacturer.objects.create(name='Samsung')
        Manufacturer.objects.create(name='Motorola')
        
        self.assertEqual(2, len(Manufacturer.objects.all()))
        
        data = {'record_ids': [2015081, 2015082]}        
        response = self.client.post(self.url_manufacturer_delete, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(2, len(Manufacturer.objects.all()))
        
        response = self.client.get(self.url_manufacturers)
        self.assertContains(response, MSG_FMT_ERROR_DELETE % 'manufacturer(s)')                

    def test_listing_truncated_to_page_size(self):
        manufacturer_names = 'A.B.C.D.E.F.G.H.I.J.K.L.M.N.O.P.Q.R.S.T.U.V.W.X.Y.Z'
        for name in manufacturer_names.split('.'):
            Manufacturer.objects.create(name=name)
        
        self.assertEqual(26, len(Manufacturer.objects.all()))
        response = self.client.get(self.url_manufacturers)
        self.assertEqual(20, len(response.context['record_list']))

    def test_explicit_page_listing(self):
        manufacturer_names = 'A.B.C.D.E.F.G.H.I.J.K.L.M.N.O.P.Q.R.S.T.U.V.W.X.Y.Z'
        for name in manufacturer_names.split('.'):
            Manufacturer.objects.create(name=name)
                
        response = self.client.get(self.url_manufacturers + '?page=2')
        self.assertEqual(6, len(response.context['record_list']))
    
    def test_updating_via_POST_request(self):
        manufacturer = Manufacturer.objects.create(name='Samsung')
        self.assertEqual(1, len(Manufacturer.objects.all()))
        
        data = {'id': manufacturer.id, 'name': 'Lenovo'}
        update_url = "%s/%s" % (self.url_manufacturer_update, data['id'])
        response = self.client.post(update_url, data=data)
    
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, 'Samsung')
        self.assertContains(response, 'Lenovo')
        
    def test_throws_404_error_trying_to_update_non_existing_record(self):
        Manufacturer.objects.create(name='Samsung')
        self.assertEqual(1, len(Manufacturer.objects.all()))
        
        data = {'id': 20587, 'name': 'Lenovo' }
        update_url = "%s/%s" % (self.url_manufacturer_update, data['id'])
        response = self.client.post(update_url, data=data)
        self.assertEqual(404, response.status_code)

    def create_test_manufacturers(self):
        Manufacturer.objects.create(name='Apple')
        Manufacturer.objects.create(name='BlackBerry')
        Manufacturer.objects.create(name='LG')
        Manufacturer.objects.create(name='Samsung')
        Manufacturer.objects.create(name='Sony')
    
    def create_test_mobile_oses(self):
        MobileOS.objects.create(name='Android')
        MobileOS.objects.create(name='BlackBerry')
        MobileOS.objects.create(name='iOS')
        MobileOS.objects.create(name='Windows Phone')
        MobileOS.objects.create(name='Tizen')
    
