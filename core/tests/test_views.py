from django.core.urlresolvers import reverse
from django.test import TestCase

from core.models import Organization, State



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
            'phone': '080-9999-1111', 'url': 'www.newdomain.com',
            'street1': 'Street.Line1', 'street2': 'Street.Line2',
            'city': 'City.Name',
        }
        resp = self.client.post(self.url_org_upd, data=data)
        self.assertEqual(302, resp.status_code)
        
        org_upd = Organization.objects.first()
        for key in data.keys():
            self.assertNotEqual(org_upd[key], org[key])
            self.asertEqual(org_upd[key], data[key])
    
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
