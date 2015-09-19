from django.contrib.messages.api import get_messages
from django.http.response import Http404
from django.test import TestCase
from django.core.urlresolvers import reverse

from enumeration.models import Manufacturer, MobileOS, Device, Team, Person, \
        MemberRole
from enumeration.forms import UNIQUE_MANUFACTURER_NAME_ERROR

from core.utils import MSG_FMT_SUCCESS_ADD, MSG_FMT_SUCCESS_DELETE, \
    MSG_FMT_ERROR_DELETE, MSG_FMT_WARN_DELETE
from core.models import BusinessOffice

from .test_models import EntityBaseTestCase



class DeviceOptionViewTest(TestCase):
    url_manufacturers = reverse('manufacturers')
    url_manufacturer_update = reverse('manufacturer-update', args=[0])
    url_manufacturer_delete = reverse('manufacturer-delete', args=[0])    
    
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
        update_url = self.url_manufacturer_update.replace('/0', "/%s" % data['id'])
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
    

class PersonViewTest(TestCase):
    url_persons = reverse('persons')    
    url_person_create = reverse('person-insert')
    url_person_update = reverse('person-update', args=[0])
    
    def test_saving_a_POST_request(self):
        office = EntityBaseTestCase.create_business_office()
        data = dict(first_name='First.Name', last_name='Last.Name',
                    gender=Person.MALE, official_status=Person.FULL_STAFF,
                    location=office.id, mobile='080-3322-1100',
                    email='info@example.org')
        resp = self.client.post(self.url_person_create, data=data)
        self.assertEqual(302, resp.status_code)        
        self.assertEqual(1, Person.objects.count())
        
    def test_updating_via_POST_request(self):
        person = self.create_person()
        data = {'id': person.id, 'first_name': 'Jane', 'last_name': 'Doe',
                'gender': Person.FEMALE, 'email': 'jane.doe@example.org', 
                'mobile': '080-2222-1111', 'location': person.location.id,
                'official_status': Person.CONTRACT_STAFF}
        update_url = self.url_person_update.replace('/0', "/%s" % data['id'])
        resp = self.client.post(update_url, data=data)
        self.assertEqual(302, resp.status_code)
        
        adjusted = Person.objects.get(pk=person.id)
        self.assertTrue(person.first_name != adjusted.first_name
                    and person.last_name == adjusted.last_name
                    and person.gender != adjusted.gender
                    and person.email != adjusted.email
                    and person.id == adjusted.id
                    and adjusted.first_name == 'Jane'
                    and adjusted.email == 'jane.doe@example.org')
    
    def test_persons_listing(self):
        self.create_persons()
        
        resp = self.client.get(self.url_persons)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(3, len(resp.context['record_list']))    
    
    @staticmethod
    def create_person():
        office = EntityBaseTestCase.create_business_office()
        return Person.objects.create(first_name='John', last_name='Doe',
            gender=Person.MALE, official_status=Person.FULL_STAFF,
            location=office, email='john.doe@example.org',
            mobile='080-3332-4441'
        )
    
    @staticmethod
    def create_persons():
        office = EntityBaseTestCase.create_business_office()
        # person 1
        Person.objects.create(first_name='John', last_name='Doe', 
            gender=Person.MALE, official_status=Person.FULL_STAFF, 
            location=office, email='john.doe@example.org', 
            mobile='080-2222-1111')
        
        # person 2
        Person.objects.create(first_name='Jane', last_name='Doe', 
            gender=Person.FEMALE, official_status=Person.FULL_STAFF, 
            location=office, email='jane.doe@example.org', 
            mobile='080-2222-3333')
        
        # person 3
        Person.objects.create(first_name='Bobby', last_name='Fisher', 
            gender=Person.MALE, official_status=Person.CONTRACT_STAFF, 
            location=office, email='b.fisher@chess.org', 
            mobile='080-9995-8884')


class MemberRoleViewTest(TestCase):
    url_roles = reverse('roles')
    url_role_create = reverse('role-insert')
    url_role_update = reverse('role-update', args=[0])
    
    def test_saving_a_POST_request(self):
        data = dict(name='Role', description='Description')
        resp = self.client.post(self.url_role_create, data=data)
        self.assertEqual(302, resp.status_code)
        self.assertEqual(1, MemberRole.objects.count())

    def test_updating_via_POST_request(self):
        roleX = MemberRole.objects.create(name='Name', description='Description')
        data = dict(name='New.Name', description='New.Description')
        upd_url = self.url_role_update.replace('/0', '/%s' % roleX.id)
        
        resp = self.client.post(upd_url, data=data)
        self.assertEqual(302, resp.status_code)
        
        roleY = MemberRole.objects.get(pk=roleX.id)
        self.assertTrue(roleX.name != roleY.name
                    and roleX.description != roleY.description
                    and roleX.id == roleY.id
                    and roleY.name == 'New.Name'
                    and roleY.description == 'New.Description')


class TeamViewTest(TestCase):
    
    fixtures = ['states', 'business-entities', 'device-options', 'devices']
    urlf_team_view = lambda s,x: reverse('team-view', args=[x])
    urlf_team_device_add = lambda s,x: reverse('team-device-add', args=[x])
    urlf_team_device_rem = lambda s,x: reverse('team-device-remove', args=[x])
    
    urlf_team_member_add = lambda s,x: reverse('team-member-add', args=[x])
    urlf_team_member_rem = lambda s,x: reverse('team-member-remove', args=[x])
    
    
    def setUp(self):
        # create teams
        tA = Team.objects.create(code='A', name='TeamA')
        Team.objects.create(code='B', name='TeamB')
        Team.objects.create(code='C', name='TeamC')
        
        d1 = Device.objects.get(pk=1)
        tA.devices.add(d1)
        
        # create member role
        MemberRole.objects.create(name='Member')
        
        # create people
        location = BusinessOffice.objects.get(name='Dakata')
        Person.objects.create(first_name='John', last_name='Doe',
            email='john.doe@example.com', mobile='080-2222-1111', 
            location=location)
        Person.objects.create(first_name='Jane', last_name='Doe',
            email='jane.doe@example.com', mobile='080-3333-2222',
            location=location)
        Person.objects.create(first_name='Ola', last_name='Sani',
            email='ola.sani@example.com', mobile='080-4444-3333',
            location=location)
    
    def test_add_device_form_has_only_unassigned_devices(self):        
        team = Team.objects.get(code='A')
        url_view = self.urlf_team_view(team.id)
        resp = self.client.get(url_view)
        self.assertEqual(200, resp.status_code)
        
        form = resp.context['devices_form']
        self.assertIsNotNone(form)
        self.assertEqual(2, len(form.fields['device'].choices))
    
    def test_adding_device_via_POST_request(self):
        team = Team.objects.get(code='A')
        url_add = self.urlf_team_device_add(team.id)
        resp = self.client.post(url_add, data={'device':'2'})
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code='A')
        self.assertEqual(2, len(team.devices.all()))
        
    def test_assigned_devices_unavailable_in_device_select_form(self):
        team = Team.objects.get(code='A')
        resp = self.client.get(self.urlf_team_view(team.id))
        form = resp.context['devices_form']
        self.assertEqual(2, len(form.fields['device'].choices))
        
        device = Device.objects.unassigned()[0]
        team.devices.add(device)

        resp = self.client.get(self.urlf_team_view(team.id))
        form = resp.context['devices_form']
        self.assertEqual(1, len(form.fields['device'].choices))
        
    def test_removing_device_via_POST_request(self):
        team = Team.objects.get(code='A')
        self.assertEqual(1, len(team.devices.all()))
        url_rem = self.urlf_team_device_rem(team.id)
        
        data = {'record_ids': team.devices.all()[0].id}
        resp = self.client.post(url_rem, data=data)
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code='A')
        self.assertEqual(0, len(team.devices.all()))
    
    def test_removed_device_isnot_deleted(self):
        team = Team.objects.get(code='A')
        self.assertEqual(1, len(team.devices.all()))
        url_rem = self.urlf_team_device_rem(team.id)
        
        device_id = team.devices.all()[0].id
        data = {'record_ids': device_id}
        resp = self.client.post(url_rem, data=data)
        self.assertEqual(302, resp.status_code)
        
        device = Device.objects.get(pk=device_id)
        self.assertIsNotNone(device)
        
    def test_add_member_form_has_only_unassigned_members(self):
        team = Team.objects.get(code='A')
        url_view = self.urlf_team_view(team.id)
        resp = self.client.get(url_view)
        self.assertEqual(200, resp.status_code)
        
        form = resp.context['members_form']
        self.assertIsNotNone(form)
        self.assertEqual(3, len(form.fields['person'].choices))
    
    def test_adding_member_via_POST_request(self):
        team = Team.objects.get(code='A')
        url_add = self.urlf_team_member_add(team.id)
        
        p = Person.objects.get(first_name='John', last_name='Doe')
        r = MemberRole.objects.get(name='Member')
        self.assertIsNotNone(r)
        
        data={'person': p.id, 'device':'1', 'role': r.id}
        resp = self.client.post(url_add, data=data)
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code='A')
        self.assertEqual(1, len(team.members.all()))

