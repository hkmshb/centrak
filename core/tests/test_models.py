from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models import State, Organization, BusinessOffice
from django.db.models.deletion import ProtectedError



class StateTestCase(TestCase):
    
    def test_can_save_and_retrieve(self):
        State.objects.create(code='ST', name='State')
        self.assertEqual(1, State.objects.count())
        
        state = State.objects.first()
        self.assertIsNotNone(state)
        self.assertTrue(state.code=='ST' and state.name=='State')
    
    def test_cannot_save_without_name(self):
        state = State(code='ST')
        with self.assertRaises(ValidationError):
            state.full_clean()
    
    def test_duplicate_names_are_invalid(self):
        State.objects.create(name='State', code='ST')
        with self.assertRaises(ValidationError):
            state = State(name='State', code='S2')
            state.full_clean()
    
    def test_duplicate_codes_are_invalid(self):
        State.objects.create(name='State', code='ST')
        with self.assertRaises(ValidationError):
            state = State(name='State2', code='ST')
            state.full_clean()
    
    def test_doesnt_have_id_field(self):
        state = State.objects.create(code='ST', name='State')
        with self.assertRaises(AttributeError):
            self.assertIsNone(state.id)
    

class OrganizationTestCase(TestCase):
    
    def test_can_save_and_retrieve(self):
        state = State.objects.create(code='ST', name='State')
        Organization.objects.create(name='Organization', 
            email='info@example.org', phone='',
            url='www.example.org',
            street1='Street1', street2='',
            city='City', state=state,
            note='Ooops!'
        )
        self.assertEqual(1, Organization.objects.count())
        
        org = Organization.objects.first()
        self.assertTrue(org.name=='Organization'
            and org.email=='info@example.org' and org.phone==''
            and org.url=='www.example.org' and org.street1=='Street1'
            and org.street2=='' and org.city=='City'
            and org.state not in (None, 0)
            and org.note=='Ooops!')
    
    def test_cannot_save_without_state(self):
        org = Organization(name='Organization', city='City')
        with self.assertRaises(ValidationError):
            org.full_clean()
        
    def test_multiple_records_unacceptable(self):
        state = State.objects.create(code='ST', name='State')
        Organization.objects.create(name='Organization', city='City', state=state)
        
        org = Organization(name='Organization 2', city='City', state=state)
        with self.assertRaises(ValidationError):
            org.full_clean()

    def test_records_protected_when_foreign_refence_gets_deleted(self):
        state = State.objects.create(code='ST', name='State')
        Organization.objects.create(name='Organization', city='City', state=state)
        self.assertEqual(1, Organization.objects.count())
        
        with self.assertRaises(ProtectedError):
            state.delete()


class BusinessOfficeTestCase(TestCase):
    
    def test_cannot_save_without_required_nonblank_fields(self):
        # required fiels omitted: name, city, and state
        office = BusinessOffice(email='biz@location.org', phone='080-5555-1111',
                    url='www.biz.org', street1='Street1', street2='Street2',
                    note='note')
        with self.assertRaises(ValidationError):
            office.full_clean()
        
    def test_duplicate_names_are_invalid(self):
        state = State.objects.create(code='ST', name='State')
        BusinessOffice.objects.create(name='Office', city='City', state=state)
        
        with self.assertRaises(ValidationError):
            office = BusinessOffice(name='Office', city='City', state=state)
            office.full_clean()
            
    def test_can_save_multiple_records(self):
        state = State.objects.create(code='sT', name='State')
        BusinessOffice.objects.create(name='Office', city='City', state=state)
        BusinessOffice.objects.create(name='Office2', city='City', state=state)
        self.assertEqual(2, BusinessOffice.objects.count())

