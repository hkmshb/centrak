from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.test import TestCase

from enumeration.models import Manufacturer, MobileOS



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
    
    