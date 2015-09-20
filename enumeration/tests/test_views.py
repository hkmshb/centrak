import re
from django.contrib.messages.api import get_messages
from django.http.response import Http404
from django.test import TestCase
from django.core.urlresolvers import reverse

from enumeration.models import Manufacturer, MobileOS, Device, Team, Person, \
        MemberRole, TeamMembership
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


# class MemberRoleViewTest(TestCase):
#     url_roles = reverse('roles')
#     url_role_create = reverse('role-insert')
#     url_role_update = reverse('role-update', args=[0])
#     
#     def test_saving_a_POST_request(self):
#         data = dict(name='Role', description='Description')
#         resp = self.client.post(self.url_role_create, data=data)
#         self.assertEqual(302, resp.status_code)
#         self.assertEqual(1, MemberRole.objects.count())
# 
#     def test_updating_via_POST_request(self):
#         roleX = MemberRole.objects.create(name='Name', description='Description')
#         data = dict(name='New.Name', description='New.Description')
#         upd_url = self.url_role_update.replace('/0', '/%s' % roleX.id)
#         
#         resp = self.client.post(upd_url, data=data)
#         self.assertEqual(302, resp.status_code)
#         
#         roleY = MemberRole.objects.get(pk=roleX.id)
#         self.assertTrue(roleX.name != roleY.name
#                     and roleX.description != roleY.description
#                     and roleX.id == roleY.id
#                     and roleY.name == 'New.Name'
#                     and roleY.description == 'New.Description')


class TeamViewTest(TestCase):
    
    fixtures = ['states', 'business-entities', 'device-options', 'devices']
    
    url_teams = reverse('teams')
    urlf_team_view = lambda s,x: reverse('team-view', args=[x])
    urlf_team_device_add = lambda s,x: reverse('team-device-add', args=[x])
    urlf_team_device_rem = lambda s,x: reverse('team-device-remove', args=[x])
    
    urlf_team_member_add = lambda s,x: reverse('team-member-add', args=[x])
    urlf_team_member_rem = lambda s,x: reverse('team-member-remove', args=[x])
    
    
    def setUp(self):
        # create teams
        self.team = Team.objects.create(code='A', name='TeamA')
        Team.objects.create(code='B', name='TeamB')
        Team.objects.create(code='C', name='TeamC')
        
        self.device = Device.objects.get(pk=1)
        self.team.devices.add(self.device)
        
        # create member role
        #MemberRole.objects.create(name='Member')
        
        # create people
        location = BusinessOffice.objects.get(name='Dakata')
        self.john = Person.objects.create(first_name='John', last_name='Doe',
                        email='john.doe@example.com', mobile='080-2222-1111', 
                        location=location)
        self.jane = Person.objects.create(first_name='Jane', last_name='Doe',
                        email='jane.doe@example.com', mobile='080-3333-2222',
                        location=location)
        self.ola = Person.objects.create(first_name='Ola', last_name='Sani',
                        email='ola.sani@example.com', mobile='080-4444-3333',
                        location=location)
    
    def test_add_device_form_has_only_unassigned_devices(self):        
        url_view = self.urlf_team_view(self.team.id)
        resp = self.client.get(url_view)
        self.assertEqual(200, resp.status_code)
        
        form = resp.context['devices_form']
        self.assertIsNotNone(form)
        self.assertEqual(2, len(form.fields['device'].choices))
    
    def test_adding_device_via_POST_request(self):
        url_add = self.urlf_team_device_add(self.team.id)
        resp = self.client.post(url_add, data={'device':'2'})
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code='A')
        self.assertEqual(2, len(team.devices.all()))
        
    def test_assigned_devices_unavailable_in_device_select_form(self):
        resp = self.client.get(self.urlf_team_view(self.team.id))
        form = resp.context['devices_form']
        self.assertEqual(2, len(form.fields['device'].choices))
        
        device = Device.objects.unassigned()[0]
        self.team.devices.add(device)

        resp = self.client.get(self.urlf_team_view(self.team.id))
        form = resp.context['devices_form']
        self.assertEqual(1, len(form.fields['device'].choices))
        
    def test_removing_device_via_POST_request(self):
        self.assertEqual(1, len(self.team.devices.all()))
        url_rem = self.urlf_team_device_rem(self.team.id)
        
        data = {'record_ids': self.team.devices.all()[0].id}
        resp = self.client.post(url_rem, data=data)
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code='A')
        self.assertEqual(0, len(team.devices.all()))
    
    def test_removed_device_isnot_deleted(self):
        self.assertEqual(1, len(self.team.devices.all()))
        url_rem = self.urlf_team_device_rem(self.team.id)
        
        device_id = self.team.devices.all()[0].id
        data = {'record_ids': device_id}
        resp = self.client.post(url_rem, data=data)
        self.assertEqual(302, resp.status_code)
        
        device = Device.objects.get(pk=device_id)
        self.assertIsNotNone(device)
        
    def test_add_member_form_has_only_unassigned_members(self):
        url_view = self.urlf_team_view(self.team.id)
        resp = self.client.get(url_view)
        self.assertEqual(200, resp.status_code)
        
        form = resp.context['members_form']
        self.assertIsNotNone(form)
        self.assertEqual(3, len(form.fields['person'].choices))
    
    def test_adding_member_via_POST_request(self):
        url_add = self.urlf_team_member_add(self.team.id)        
        data={'person': self.john.id, 'device':'1', 'role': MemberRole.ENUMERATOR}
        resp = self.client.post(url_add, data=data)
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code='A')
        self.assertEqual(1, len(team.members.all()))

    def test_device_choices_has_empty_entry(self):
        url_view = self.urlf_team_view(self.team.id)
        resp = self.client.get(url_view)
        self.assertEqual(200, resp.status_code)
        
        form = resp.context['members_form']
        self.assertEqual(1, len(self.team.devices.all()))
        self.assertEqual(len(form.fields['device'].choices),
                         len(self.team.devices.all()) + 1)
        self.assertEqual(form.fields['device'].choices[0], ('0', 'None'))

    def test_device_cannot_be_assigned_to_multiple_members(self):
        urlf_add = self.urlf_team_member_add(self.team.id)
        
        # first member
        data = {'person': self.john.id, 'device':'1', 'role': MemberRole.ENUMERATOR}
        resp = self.client.post(urlf_add, data=data)
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code='A')
        self.assertEqual(1, len(team.members.all()))
        
        # proposed second member; addition should fail
        data = {'person': self.jane.id, 'device':'1', 'role':MemberRole.ENUMERATOR}
        resp = self.client.post(urlf_add, data=data)
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code='A')
        self.assertNotEqual(2, len(team.members.all())) 
    
    def test_device_can_only_be_assigned_to_enumerator(self):
        urlf_add = self.urlf_team_device_add(self.team.id)
        
        data = {'person':self.john.id, 'device':'1', 'role': MemberRole.MEMBER}
        resp = self.client.post(urlf_add, data=data)
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code='A')
        self.assertEqual(0, len(team.members.all()))
    
    def test_can_add_non_enumerator_without_device(self):
        urlf_add = self.urlf_team_member_add(self.team.id)
        data = {'person':self.john.id, 'device': '0', 'role': MemberRole.MEMBER}
        resp = self.client.post(urlf_add, data=data)
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code='A')
        self.assertEqual(1, len(team.members.all()))

    def test_cannot_add_enumerator_without_device(self):
        url_add = self.urlf_team_member_add(self.team.id)
        data = {'person':self.john.id, 'device':'0', 'role':MemberRole.ENUMERATOR}
        resp = self.client.post(url_add, data=data)
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code='A')
        self.assertEqual(0, len(team.members.all()))

    def test_member_assigned_team_device_not_available_in_form(self):
        url_detail = self.urlf_team_view(self.team.id)
        resp = self.client.get(url_detail)
        form = resp.context['members_form']
        self.assertEqual(2, len(form.fields['device'].choices))
        
        # assign enumerator to team
        TeamMembership.objects.create(team=self.team, person=self.john,
            device=self.device, role=MemberRole.ENUMERATOR)
        
        resp = self.client.get(url_detail)
        choices = resp.context['members_form'].fields['device'].choices
        self.assertEqual(1, len(choices))
        self.assertEqual(('0', 'None'), choices[0])

    def test_removing_member_via_POST_request(self):
        TeamMembership.objects.create(team=self.team, person=self.john,
            device=self.device, role=MemberRole.ENUMERATOR)
        
        team = Team.objects.get(code=self.team.code)
        self.assertEqual(1, len(team.members.all()))
        
        url_rem = self.urlf_team_member_rem(self.team.id)        
        resp = self.client.post(url_rem, data={'record_ids': self.john.id})
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code=self.team.code)
        self.assertEqual(0, len(team.members.all()))
        
    def test_removed_member_isnot_deleted(self):
        TeamMembership.objects.create(team=self.team, person=self.john,
            device=self.device, role=MemberRole.ENUMERATOR)
        
        team = Team.objects.get(code=self.team.code)
        self.assertEqual(1, len(team.members.all()))        
        
        url_rem = self.urlf_team_member_rem(self.team.id)
        resp = self.client.post(url_rem, data={'record_ids': self.john.id})
        self.assertEqual(302, resp.status_code)
        
        team = Team.objects.get(code=self.team.code)
        self.assertEqual(0, len(team.members.all()))        
        
        # ensure member still exist
        person = Person.objects.get(pk=self.john.id)
        self.assertIsNotNone(person)

    def test_team_with_devices_only_has_correct_count_summaries(self):
        # self.team has no members but one device assigned
        self.assertTrue(self.team.members.count() == 0 
                    and self.team.devices.count() == 1)
        
        resp = self.client.get(self.url_teams)
        list_ = list(resp.context['record_list'])
        self.assertEqual(3, len(list_))
        self.assertTrue(list_[0].code == 'A' 
                    and list_[0].name == 'TeamA'
                    and list_[0].members.count() == 0
                    and list_[0].devices.count() == 1)
        
        tr = self.re_find(resp.content, '<tbody>.+<tr>.+</tr>')
        self.assertTrue(tr.find('<td>A</td>') != -1
                    and tr.find('TeamA') != -1
                    and tr.find('<td>0</td>') != -1
                    and tr.find('<td>1</td>') != -1)        
    
    def test_team_with_devices_and_members_has_correct_count_summaries(self):
        TeamMembership.objects.create(team=self.team, person=self.john,
            role=MemberRole.MEMBER)
        
        resp = self.client.get(self.url_teams)
        list_ = list(resp.context['record_list'])
        self.assertEqual(3, len(list_))
        self.assertTrue(list_[0].code == 'A' 
                    and list_[0].name == 'TeamA'
                    and list_[0].members.count() == 1
                    and list_[0].devices.count() == 1)
        
        tr = self.re_find(resp.content, '<tbody>.+<tr>.+</tr>')
        self.assertTrue(tr.find('<td>A</td>') != -1
                    and tr.find('TeamA') != -1
                    and tr.find('<td>1</td>') != -1
                    and tr.find('<td>1</td>') != -1)    
    
    def re_find(self, content, pattern):
        m = re.search(pattern, content.decode(), re.DOTALL)
        self.assertIsNotNone(m)
        return m.group(0)
