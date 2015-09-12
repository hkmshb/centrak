from django.core.exceptions import ValidationError
from django.test import TestCase

from enumeration.models import Manufacturer, MobileOS, Device, DeviceIMEI, \
     Person, Team, MemberRole
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
        person = Person.objects.create(first_name='John', last_name='Doe',
                    gender=Person.MALE, official_status=Person.FULL_STAFF,
                    email='info@example.com', mobile='080-2222-1111',
                    location=office)
        self.assertTrue(person.id > 0)
        self.assertTrue(person.is_active)
    
    def test_person_deletion_only_sets_is_active_to_false(self):
        self.fail('write test')
        

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
    

class MemberRoleTest(TestCase):
    
    def test_duplicate_name_are_invalid(self):
        MemberRole.objects.create(name='Name', description='Description')
        with self.assertRaises(ValidationError):
            role = MemberRole(name='Name', description='New.Description')
            role.full_clean()

        