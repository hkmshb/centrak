from django.core.urlresolvers import reverse
from django.test import TestCase

from core.models import Organization, State, BusinessOffice



class OrganizationViewTest(TestCase):
    url_org_info = reverse('org-info')
    url_org_upd = reverse('org-update')
    
    def test_org_page_displays_info_and_offices(self):
        self.create_organization()
        resp = self.client.get(self.url_org_info)
        self.assertEqual(200, resp.status_code)
        
        ctxt = resp.context
        self.assertIsNotNone(ctxt['organization'])
        self.assertIsNotNone(ctxt['biz_offices'])
    
    def test_can_update_org_info(self):
        org = self.create_organization()
        data = {'name': 'Org.Name', 'email': 'new_box@example.com',
            'phone': '080-9999-1111', 'url': 'http://newdomain.com/',
            'street1': 'Street.Line1', 'street2': 'Street.Line2',
            'city': 'City.Name', 'state': 'ST'
        }
        resp = self.client.post(self.url_org_upd, data=data)
        self.assertEqual(302, resp.status_code)
        
        org_upd = Organization.objects.first()
        org2_data = self.build_org_dict(org_upd) 
        org1_data = self.build_org_dict(org)
        
        for key in [k for k in  data.keys() if k != 'state']:
            self.assertNotEqual(org1_data[key], org2_data[key])
            self.assertEqual(org2_data[key], data[key])
        
    def create_organization(self):
        org = self.build_organization()
        org.save()
        return org
    
    def build_organization(self):
        return Organization(
            name='Organization', email='info@example.org',
            phone='080-5555-1111', url='www.example.org',
            street1='Street1', street2='Street2',
            city='City', state=State.objects.create(code='ST', name='State')
        )
    
    def build_org_dict(self, org):
        return {
            'name': org.name, 'email': org.email,
            'phone': org.phone, 'url': org.url,
            'street1': org.street1, 'street2': org.street2,
            'city': org.city, 'state': org.state
        }

class BusinessOfficeViewTest(TestCase):
    url_office_new = reverse('office-create')
    url_office_upd = reverse('office-update', args=[0])    
    
    def test_can_create_biz_office(self):
        State.objects.create(code='ST', name='State', capcity='CapCity')
        data = {'name': 'Biz.Office', 'email': 'biz_office@example.com',
            'phone': '080-2222-1111', 'url': 'http://office.newdomain.com/',
            'city':'City.Name', 'state': 'ST'
        }
        resp = self.client.post(self.url_office_new, data=data)
        self.assertEqual(302, resp.status_code)
        
        count = BusinessOffice.objects.count()
        self.assertEqual(1, count)

    def test_can_update_biz_office(self):
        state = State.objects.create(code='ST', name='State', capcity='CapCity')
        office = BusinessOffice.objects.create(name='Biz.Office',
                    email='biz_office@example.com', url='http://office.example.com/',
                    phone='080-2222-1111', city='CityA', state=state)
        count = BusinessOffice.objects.count()
        self.assertTrue(office.id != 0)
        self.assertEqual(1, count)
        
        office_update = {'name': 'Biz2.Office', 'city': 'CityB', 'state':'ST'}
        url = self.url_office_upd.replace('/0', '/%s' % office.id)
        resp = self.client.post(url, data=office_update)
        
        self.assertEqual(302, resp.status_code)        
        self.assertEqual(1, BusinessOffice.objects.count())
        
        updated_office = BusinessOffice.objects.get(pk=office.id)
        self.assertTrue(office.name != updated_office.name
                    and office.city != updated_office.city
                    and updated_office.name == office_update['name']
                    and updated_office.city == office_update['city'])
    
