from django.core.exceptions import ValidationError
from django.test import TestCase

from enumeration.models import Manufacturer, MobileOS, Device, DeviceIMEI, \
     Person, Team, MemberRole, TeamMembership, Group
from core.models import State, BusinessOffice




class ManufacturerTest(TestCase):
    
    def test_duplicate_manufacturer_are_invalid(self):
        Manufacturer.objects.create(name='Samsung')
        with self.assertRaises(ValidationError):
            manufacturer = Manufacturer(name='Samsung')
            manufacturer.full_clean()


class MobileOSTest(TestCase):
    
    def test_duplicate_mobileos_are_invalid(self):
        MobileOS.objects.create(name='Android', provider='Google')
        with self.assertRaises(ValidationError):
            os = MobileOS(name='Android')
            os.full_clean()


class DeviceBaseTestCase(TestCase):
    
    def build_device(self):
        brand = Manufacturer.objects.create(name='Samsung')
        mobile_os = MobileOS.objects.create(name='Android')
        return Device(
            label = 'T01D01',
            brand = brand,
            model = 'Device Model',
            mobile_os = mobile_os,
            os_version = '1.0.0 (whatever)',
            form_factor = Device.PHONE,
            serialno = ''
        )
    
    def build_device_without_brand(self):
        mobile_os = MobileOS.objects.create(name='Android')
        return Device(
            model = 'Device Model',
            mobile_os = mobile_os,
            os_version = '1.0.0 (whatever)',
            form_factor = Device.PHONE,
            serialno = ''
        )
    
    def build_device_without_mobile_os(self):
        brand = Manufacturer.objects.create(name='Samsung')
        return Device(
            brand = brand,
            model = 'Device Model',
            os_version = '1.0.0 (whatever)',
            form_factor = Device.PHONE,
            serialno = ''
        )


class DeviceTest(DeviceBaseTestCase):
    
    def test_cannot_save_without_brand(self):
        device = self.build_device_without_brand()
        with self.assertRaises(ValidationError):
            device.full_clean()
     
    def test_cannot_save_without_mobile_os(self):
        device = self.build_device_without_mobile_os()
        with self.assertRaises(ValidationError):
            device.full_clean()
    
    def test_blank_serialno_allowed(self):
        device = self.build_device()
        device.serial_no = ''
        device.full_clean()


class DeviceIMEITest(DeviceBaseTestCase):
    
    def test_duplicate_imei_are_invalid(self):
        device = self.build_device()
        device.save()
        
        DeviceIMEI.objects.create(device=device, imei='35010203040506070809')
        with self.assertRaises(ValidationError):
            imei = DeviceIMEI(device=device, imei='35010203040506070809')
            imei.full_clean()
    
    def test_blank_imei_not_allowed(self):
        device = self.build_device()
        device.save()
        
        with self.assertRaises(ValidationError):
            imei = DeviceIMEI(device=device)
            imei.full_clean()
    
    def test_returns_meaningful_string_repr(self):
        imei = DeviceIMEI(self.build_device(), imei='35010203040506070809')
        self.assertEqual('imei=35010203040506070809', str(imei))


class EntityBaseTestCase(TestCase):
    
    def build_person(self):
        office = self.create_business_office()
        return Person(
            first_name='First.Name', last_name='Last.Name',
            gender=Person.MALE, official_status=Person.FULL_STAFF,
            location=office, mobile='080-2222-1111',
            email='info@example.org')
    
    @staticmethod
    def create_business_office():
        office = EntityBaseTestCase.get_business_office()
        office.save()
        return office
    
    @staticmethod
    def get_business_office():
        state = State.objects.create(code='ST', name='State')
        return BusinessOffice(name='Biz.Office', city='City',
                state=state)
    

class PersonTest(EntityBaseTestCase):
    
    fixtures = ['states', 'business-entities']

    @staticmethod
    def person_setup(self):
        # create person
        location = BusinessOffice.objects.get(name='Dakata')
        self.john = Person.objects.create(first_name='John', last_name='Doe',
                        email='john.doe@example.com', mobile='080-2222-1111', 
                        location=location)
        self.jane = Person.objects.create(first_name='Jane', last_name='Doe',
                        email='jane.doe@example.com', mobile='080-3333-2222',
                        location=location)     
    
    def setUp(self):
        self.person_setup(self)
    
    def test_cannot_save_without_nonblank_fields(self):
        office = self.create_business_office()
        person = Person(gender=Person.MALE, official_status=Person.FULL_STAFF,
                        location=office)
        with self.assertRaises(ValidationError):
            person.full_clean()
    
    def test_duplicate_first_last_names_are_invalid(self):
        office = self.create_business_office()
        Person.objects.create(first_name='First.Name', last_name='Last.Name',
                              official_status=Person.FULL_STAFF, location=office,
                              mobile='080-2222-1111', email='info@example.org')
        with self.assertRaises(ValidationError):
            p = Person(first_name='First.Name', last_name='Last.Name',
                       official_status=Person.INDUSTRIAL_TRAINEE,
                       location=office, mobile='080-3333-2222',
                       email='info@example.org')
            p.full_clean()
    
    def test_new_person_active_by_default(self):
        office = self.create_business_office()
        person = Person.objects.create(first_name='John', last_name='Snow',
                    gender=Person.MALE, official_status=Person.FULL_STAFF,
                    email='john.snow@example.com', mobile='080-2222-1111',
                    location=office)
        self.assertTrue(person.id > 0)
        self.assertTrue(person.is_active)
    
    def test_person_deletion_only_sets_is_active_to_false(self):
        self.fail('write test')

    def test_implicit_listing_provides_active_persons_only(self):
        # add in active person
        Person.objects.create(first_name='Bob', last_name='Rob',
            email='bob.rob@example.com', mobile='070-9999-8888',
            location=BusinessOffice.objects.get(name='Dakata'),
            is_active=False)
        self.assertEqual(2, Person.objects.all().count())
        self.assertEqual(3, Person.objects.all(include_inactive=True).count())

class TeamTest(TestCase):
    
    def test_cannot_save_without_nonblank_fields(self):
        with self.assertRaises(ValidationError):
            team = Team()
            team.full_clean()
    
    def test_new_team_active_by_default(self):
        team = Team(code='Code', name='Name')
        self.assertTrue(team.is_active)
    
    def test_duplicate_codes_are_invalid(self):
        Team.objects.create(code='Code', name='Name')
        with self.assertRaises(ValidationError):
            team = Team(code='Code', name='Diff.Name')
            team.full_clean()
    
    def test_duplicate_name_are_invalid(self):
        Team.objects.create(code='Code', name='Name')
        with self.assertRaises(ValidationError):
            team = Team(code='New.Code', name='Name')
            team.full_clean()
    
    def test_team_deletion_only_sets_is_active_to_false(self):
        self.fail('write test')


class TeamMembershipTest(TestCase):    
    
    fixtures = ['states', 'business-entities', 'device-options', 'devices']
    
    @staticmethod
    def membership_setup(self):
        # create teams
        self.team = Team.objects.create(code='A', name='Team-A')
        Team.objects.create(code='B', name='Team-B')
        Team.objects.create(code='C', name='Team-C')
        
        # assign device
        self.device = Device.objects.get(pk=1)
        self.team.devices.add(self.device)
        
        # create person
        location = BusinessOffice.objects.get(name='Dakata')
        self.john = Person.objects.create(first_name='John', last_name='Doe',
                        email='john.doe@example.com', mobile='080-2222-1111', 
                        location=location)
        self.jane = Person.objects.create(first_name='Jane', last_name='Doe',
                        email='jane.doe@example.com', mobile='080-3333-2222',
                        location=location)        

    def setUp(self):
        self.membership_setup(self)
    
    def test_enumerator_must_be_assigned_device(self):
        t, p = (self.team, self.john)
        with self.assertRaises(ValidationError):
            r = MemberRole.ENUMERATOR
            m = TeamMembership(team=t, person=p, role=r)
            m.full_clean()
    
    def test_cannot_assign_device_to_non_enumerator(self):
        t, d, p = (self.team, self.device, self.john)
        with self.assertRaises(ValidationError):
            r = MemberRole.MEMBER
            m = TeamMembership(team=t, person=p, device=d, role=r)
            m.full_clean()
    
    def test_cannot_assign_team_device_to_multiple_members(self):
        t, d, p = (self.team, self.device, self.john)
        r = MemberRole.ENUMERATOR
        
        TeamMembership.objects.create(team=t, person=p, device=d, role=r)
        with self.assertRaises(ValidationError):
            p = Person.objects.get(first_name='Jane')
            m = TeamMembership(team=t, person=p, device=d, role=r)
            m.full_clean()
    
    def test_can_add_multiple_enumerators(self):
        # NOTE: the TeamMember model logic which prevents multiple assignment
        # o same device is ill-formed as this prevents the addition of another
        # enumerator to the team. Hence the need to test that a team can be
        # assigned multiple enumerators!
        t, d, john, jane = (self.team, self.device, self.john, self.jane)
        d2 = Device.objects.get(pk=2)
        r = MemberRole.ENUMERATOR
        self.assertEqual(0, len(t.members.all()))
        
        TeamMembership.objects.create(team=t, person=john, device=d, role=r)        
        tm = TeamMembership(team=t, person=jane, device=d2, role=r)
        tm.full_clean()
        tm.save()
        
        t2 = Team.objects.get(code=t.code)
        self.assertEqual(2, len(t2.members.all()))
    
    def test_implicit_listing_provides_active_teams_only(self):
        # add inactive group
        Team.objects.create(code='D', name='Team-D', is_active=False)
        self.assertEqual(3, Team.objects.all().count())
        self.assertEqual(4, Team.objects.all(include_inactive=True).count())
        

# class MemberRoleTest(TestCase):
#     
#     def test_duplicate_name_are_invalid(self):
#         MemberRole.objects.create(name='Name', description='Description')
#         with self.assertRaises(ValidationError):
#             role = MemberRole(name='Name', description='New.Description')
#             role.full_clean()


class GroupTest(TestCase):

    fixtures = ['states', 'business-entities']

    @staticmethod
    def group_setup(self):
        # create person
        location = BusinessOffice.objects.get(name='Dakata')
        self.john = Person.objects.create(first_name='John', last_name='Doe',
                        email='john.doe@example.com', mobile='080-2222-1111', 
                        location=location)
        self.jane = Person.objects.create(first_name='Jane', last_name='Doe',
                        email='jane.doe@example.com', mobile='080-3333-2222',
                        location=location)  
        
        # create teams
        self.team = Team.objects.create(code='A', name='Team-A')
        Team.objects.create(code='B', name='Team-B')
        Team.objects.create(code='C', name='Team-C')
    
    def setUp(self):
        self.group_setup(self)

    def test_duplicate_name_are_invalid(self):
        Group.objects.create(name='GroupA', supervisor=self.john)
        with self.assertRaises(ValidationError):
            group = Group(name='GroupA', supervisor=self.john)
            group.full_clean()
    
    def test_cannot_save_without_supervisor(self):
        with self.assertRaises(Exception):
            group = Group(name='GroupA')
            group.full_clean()
    
    def test_cant_assign_same_person_to_supervise_multiple_groups(self):
        Group.objects.create(name='GroupA', supervisor=self.john)
        with self.assertRaises(ValidationError):
            group = Group(name='GroupB', supervisor=self.john)
            group.full_clean()
        
    def test_cant_assign_person_with_function_as_supervisor(self):
        # make john member of team A
        TeamMembership.objects.create(team=self.team, person=self.john,
            role=MemberRole.MEMBER)
        
        # now try making john a group supervisor; should fail
        with self.assertRaises(ValidationError):
            group = Group(name='GroupA', supervisor=self.john)
            group.full_clean()
    
    def test_implicit_listing_provides_active_groups_only(self):
        # setup group entries
        Group.objects.create(name='GroupA', supervisor=self.john)
        Group.objects.create(name='GroupB', supervisor=self.jane, is_active=False)
        self.assertEqual(1, Group.objects.all().count())
        self.assertEqual(2, Group.objects.all(include_inactive=True).count())


