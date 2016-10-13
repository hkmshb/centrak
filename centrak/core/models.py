from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models

from ezaddress.models import Addressable, GPSLocatable
from .exceptions import InvalidOperationError


class TimeStampedModel(models.Model):
    """
    Abstract base model with fields for tracking object creation and last
    update dates.
    """
    date_created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True, null=True)

    class Meta:
        abstract = True


class BusinessEntity(TimeStampedModel, Addressable, GPSLocatable):
    """
    Abstract base class which represents a Business entity.
    """
    name    = models.CharField(_('Name'), max_length=40, unique=True)
    email   = models.EmailField(_('Email'), max_length=100, blank=True)
    phone   = models.CharField(_('Phone'), max_length=20, blank=True)
    website = models.URLField(_('Website'), max_length=100, blank=True)

    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name


class BusinessLevel(models.Model):
    """
    Represents the level of a Business Office within an the hierarchical 
    structure.
    """
    LEVEL1 = 'L1'
    LEVEL2 = 'L2'
    LEVEL3 = 'L3'
    LEVEL_CHOICES = (
        (LEVEL1, 'Level-1'),
        (LEVEL2, 'Level-2'),
        (LEVEL3, 'Level-3')
    )
    
    code = models.CharField(_('Code'), primary_key=True, max_length=2, 
                choices=LEVEL_CHOICES)
    name = models.CharField(_('Name'), max_length=20, unique=True)
    
    class Meta:
        db_table = 'business_level'
    
    def __str__(self):
        return self.name


class Organisation(BusinessEntity):
    """
    Represents the organisation performing customer enumeration tracking.
    
    Only a single record can exist. Once created it cannot be deleted, though
    it can be updated. Creation of additional records would result to an error. 
    """
    
    _error_messages = {
        'multiple-records': _('Multiple records cannot be stored for Organisation.'),
    }
    
    short_name = models.CharField(_('Short Name'), max_length=20, blank=True)

    class Meta:
        db_table = 'organisation'
    
    def _process_instance(self):
        """
        Determines whether to allow the processing of an instance if it wouldn't 
        result in the creation of multiple entries for Organisation.
        
        An instance with an id can be safely processed as it already exist. An
        instance without an id is only safe for processing if a record does not
        already exist.
        """
        return self.id or Organisation.objects.count() == 0
    
    def clean(self):
        # Ensure only a single entry/record can be stored
        super(Organisation, self).clean()
        if not self._process_instance():
            raise ValidationError(self._error_messages['multiple-records'])
    
    def save(self, *args, **kwargs):
        # permit all updates; permit save iff no record already exist
        if not self._process_instance():
            message = self._error_messages['multiple-records']
            raise InvalidOperationError(message)
        super(Organisation, self).save(*args, **kwargs)


class BusinessOffice(BusinessEntity):
    """
    Represents a business office maintained by an organisation.
    """
    CUSTOMER_SERVICE_POINT = 'CSP'
    TECHNICAL_SERVICE_POINT = 'TSP'
    SERVICE_POINT_CHOICES = (
        (CUSTOMER_SERVICE_POINT, 'Customer Service Point'),
        (TECHNICAL_SERVICE_POINT, 'Technical Service Point'),
    )

    code   = models.CharField(_('Code'), max_length=12, unique=True)
    level  = models.ForeignKey(BusinessLevel, verbose_name=_('Level'), 
                null=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey('self', verbose_name=_('Parent Office'),
                blank=True, null=True, on_delete=models.SET_NULL)
    category = models.CharField(_('Category'), max_length=5, blank=True,
                choices=SERVICE_POINT_CHOICES)
    
    _error_messages = {
        'root-has-parent': _("Business Office at Level-1 cannot have parent."),
        'parent-child-same-level': _("Parent and child Business Offices cannot "
                                     "be at the same Business Level."),
        'category-required': _("Business Office at Level-2 must have Category."),
        'category-not-required': _("Business Office at this level cannot have Category")
    }
    
    class Meta:
        db_table = 'business_office'
        ordering = ['level', 'name']
    
    def clean(self):
        super(BusinessOffice, self).clean()
        if self.level:
            if self.level.code == BusinessLevel.LEVEL1 and self.parent:
                message = self._error_messages['root-has-parent']
                raise ValidationError(message)
            
            if self.parent and self.parent.level:
                if self.level.code == self.parent.level.code:
                    message = self._error_messages['parent-child-same-level']
                    raise ValidationError(message)
            
            if self.level.code == BusinessLevel.LEVEL2:
                if self.category in (None, ""):
                    message = self._error_messages['category-required']
                    raise ValidationError(message)
            else:
                if self.category not in (None, ""):
                    message = self._error_messages['category-not-required']
                    raise ValidationError(message)
