import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from ..models import BusinessLevel, Organisation, BusinessOffice
from ..exceptions import InvalidOperationError



@pytest.mark.django_db
class TestBusinessLevel(object):
    
    def test_can_create_for_valid_code_with_name(self):
        if BusinessLevel.objects.count() == 0:
            obj = BusinessLevel(code='L1', name='Level 1')
            obj.save()
            
            assert BusinessLevel.objects.count() == 1
    
    def test_creation_fails_for_code_not_specified_in_choices(self):
        code = 'XY'
        level_choices = [choice[0] for choice in BusinessLevel.LEVEL_CHOICES]
        
        assert code not in level_choices
        
        obj = BusinessLevel(code=code, name='Level XY')
        with pytest.raises(ValidationError):
            obj.full_clean()
    
    def test_creation_fails_for_duplicate_code(self):
        # BusinessLevel.objects.create(code='L1', name='Level 1')
        obj = BusinessLevel(code='L1', name='Level X')
        with pytest.raises(ValidationError):
            obj.full_clean()


@pytest.mark.django_db
class TestOrganisation(object):
    
    def test_allows_single_record_entry(self):
        assert Organisation.objects.count() == 0
        org = Organisation(name='Sample Organization')
        org.save()
        
        assert Organisation.objects.count() == 1
    
    def test_validation_fails_for_intended_additional_record(self):
        assert Organisation.objects.count() == 0
        Organisation.objects.create(name='Sample Organization')
        
        org = Organisation(name='Sample Organization 2')
        with pytest.raises(ValidationError):
            org.full_clean()
    
    def test_fails_when_saving_intended_additional_record(self):
        assert Organisation.objects.count() == 0
        Organisation.objects.create(name='Sample Organization')
        with pytest.raises(InvalidOperationError):
            Organisation.objects.create(name='Sample Organization 2')


@pytest.mark.django_db
class TestBusinessOffice(object):
    
    def _create_business_levels(self):
        # no need to create any more objects here as required objects are 
        # created when applying a migration...
        self._level1 = BusinessLevel.objects.get(code='L1')
        self._level2 = BusinessLevel.objects.get(code='L2')
    
    def test_sublevel_office_can_have_null_parent(self):
        self._create_business_levels()
        
        assert BusinessOffice.objects.count() == 0
        office = BusinessOffice(
            code='BO1', 
            name='Office', 
            level=self._level2,
            category=BusinessOffice.CUSTOMER_SERVICE_POINT
        )
        
        office.full_clean()
        office.save()
        
        assert BusinessOffice.objects.count() == 1
    
    def test_sublevel_office_can_be_assigned_parent_of_higher_level(self):
        self._create_business_levels()
        
        assert BusinessOffice.objects.count() == 0
        office = BusinessOffice.objects.create(
            code='BO1',
            name='Office',
            level=self._level1
        )
        
        sub_office = BusinessOffice(
            code='BO1-1',
            name='Sub Office',
            level=self._level2,
            parent=office,
            category=BusinessOffice.CUSTOMER_SERVICE_POINT
        )
        
        sub_office.full_clean()
        sub_office.save()
        assert BusinessOffice.objects.count() == 2
    
    def test_validation_fails_for_Level1_office_with_parent(self):
        self._create_business_levels()
        
        assert BusinessOffice.objects.count() == 0
        office1 = BusinessOffice.objects.create(
            code='BO1',
            name='Office',
            level=self._level1
        )
        
        office2 = BusinessOffice(
            code='BO2',
            name='Office 2',
            level=self._level1,
            parent=office1
        )
        
        with pytest.raises(ValidationError):
            office2.full_clean()
    
    def test_validation_fails_for_parent_with_same_level_as_instance(self):
        self._create_business_levels()
        
        office1 = BusinessOffice.objects.create(
            code='BO1',
            name='Office',
            level=self._level2
        )
        
        office2 = BusinessOffice(
            code='BO2',
            name='Office 2', 
            level=self._level2,
            parent=office1
        )
        
        with pytest.raises(ValidationError):
            office2.full_clean()
    
    def test_creation_fails_for_non_unique_code(self):
        self._create_business_levels()
        
        BusinessOffice.objects.create(code='BO1', name='Office', level=self._level1)
        with pytest.raises(IntegrityError):
            BusinessOffice.objects.create(
                code='BO1', 
                name='Office 2', 
                level=self._level1
            )
    
    def test_creation_fails_for_non_unique_name(self):
        self._create_business_levels()
        
        BusinessOffice.objects.create(code='BO1', name='Office', level=self._level1)
        with pytest.raises(IntegrityError):
            BusinessOffice.objects.create(
                code='BO2', 
                name='Office', 
                level=self._level1
            )
    
    def test_valdiation_fails_for_level2_without_category(self):
        self._create_business_levels()
        office = BusinessOffice(
            code='B01S01',
            name='Sub Office 1',
            level=self._level2,
        )

        with pytest.raises(ValidationError):
            office.full_clean()
    
    def test_validation_fails_for_non_level2_with_category(self):
        self._create_business_levels()
        office = BusinessOffice(
            code='B01',
            name='Office 1',
            level=self._level1,
            category=BusinessOffice.CUSTOMER_SERVICE_POINT
        )

        with pytest.raises(ValidationError):
            office.full_clean()
    
    def test_level2_office_can_have_category(self):
        self._create_business_levels()
        office = BusinessOffice(
            code='B01S01',
            name='Sub Office 1',
            level=self._level2,
            category=BusinessOffice.CUSTOMER_SERVICE_POINT
        )

        office.full_clean()
        office.save()
        assert BusinessOffice.objects.count() == 1
