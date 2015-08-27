from django.core.exceptions import ValidationError
from django.test import TestCase

from enumeration.models import Manufacturer, MobileOS, Device, DeviceIMEI



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
    

class DeviceTest(TestCase):
    
    def test_cannot_save_without_brand(self):
        device = build_device_without_brand()
        with self.assertRaises(ValidationError):
            device.full_clean()
     
    def test_cannot_save_without_mobile_os(self):
        device = build_device_without_mobile_os()
        with self.assertRaises(ValidationError):
            device.full_clean()
    
    def test_blank_serialno_allowed(self):
        device = build_device()
        device.serial_no = ''
        device.full_clean()        


class DeviceIMEITest(TestCase):
    
    def test_duplicate_imei_are_invalid(self):
        device = build_device()
        device.save()
        
        DeviceIMEI.objects.create(device=device, imei='35010203040506070809')
        with self.assertRaises(ValidationError):
            imei = DeviceIMEI(device=device, imei='35010203040506070809')
            imei.full_clean()
    
    def test_blank_imei_not_allowed(self):
        device = build_device()
        device.save()
        
        with self.assertRaises(ValidationError):
            imei = DeviceIMEI(device=device)
            imei.full_clean()
    
    def test_returns_meaningful_string_repr(self):
        imei = DeviceIMEI(build_device(), imei='35010203040506070809')
        self.assertEqual('imei=35010203040506070809', str(imei))
       

class ParticipantTest(TestCase):
    pass


def build_device():
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


def build_device_without_brand():
    mobile_os = MobileOS.objects.create(name='Android')
    return Device(
        model = 'Device Model',
        mobile_os = mobile_os,
        os_version = '1.0.0 (whatever)',
        form_factor = Device.PHONE,
        serialno = ''
    )


def build_device_without_mobile_os():
    brand = Manufacturer.objects.create(name='Samsung')
    return Device(
        brand = brand,
        model = 'Device Model',
        os_version = '1.0.0 (whatever)',
        form_factor = Device.PHONE,
        serialno = ''
    )    