from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models

from mongoengine import Document, fields

from ezaddress.models import Addressable, GPSLocatable
from core.exceptions import InvalidOperationError



class TimeStampedModel(models.Model):
    """
    An abstract base model with fields for tracking object creation and last 
    update dates.
    """
    date_created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True, null=True)
    
    class Meta:
        abstract = True


class BusinessEntity(TimeStampedModel, Addressable, GPSLocatable):
    """
    An abstract base class which represents a Business entity.
    """
    name    = models.CharField(_('Name'), max_length=40, unique=True)
    email   = models.EmailField(_('Email'), max_length=100, blank=True)
    phone   = models.CharField(_('Phone'), max_length=20, blank=True)
    website = models.CharField(_('Website'), max_length=100, blank=True)
    
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
        (LEVEL1, 'Level 1'),
        (LEVEL2, 'Level 2'),
        (LEVEL3, 'Level 3')
    )
    
    code = models.CharField(_('Code'), primary_key=True, max_length=2, 
                choices=LEVEL_CHOICES)
    name = models.CharField(_('Name'), max_length=20, unique=True)
    
    class Meta:
        db_table = 'business_level'
    
    def __str__(self):
        return "({}) {}".format(self.code, self.name)


class Organization(BusinessEntity):
    """
    Represents the organization performing customer enumeration tracking.
    
    Only a single record can exist. Once created it cannot be deleted, though
    it can be updated. Creation of additional records would result to an error. 
    """
    
    _error_messages = {
        'multiple-records': _('Multiple records cannot be stored for Organization.'),
    }
    
    class Meta:
        db_table = 'organization'
    
    def to_dict(self):
        return dict(id=self.id,
            name=self.name, email=self.email, phone=self.phone,
            website=self.website, addr_street=self.addr_street,
            addr_town=self.addr_town, postal_code=self.postal_code,
            addr_raw=self.addr_raw,
            addr_state=(self.addr_state.id if self.addr_state else 0),
            date_created=self.date_created.strftime('%Y-%m-%d'), 
            last_updated=self.last_updated.strftime('%Y-%m-%d')
        )

    def _process_instance(self):
        """
        Determines whether to allow the processing of an instance if it wouldn't 
        result in the creation of multiple entries for Organization.
        
        An instance with an id can be safely processed as it already exist. An
        instance without an id is only safe for processing if a record does not
        already exist.
        """
        return self.id or Organization.objects.count() == 0
    
    def clean(self):
        # Ensure only a single entry/record can be stored
        super(Organization, self).clean()
        if not self._process_instance():
            raise ValidationError(self._error_messages['multiple-records'])
    
    def save(self, *args, **kwargs):
        # permit all updates; permit save iff no record already exist
        if not self._process_instance():
            message = self._error_messages['multiple-records']
            raise InvalidOperationError(message)
        super(Organization, self).save(*args, **kwargs)


class BusinessOffice(BusinessEntity):
    code = models.CharField(_('Code'), max_length=5, unique=True)
    level = models.ForeignKey(BusinessLevel, verbose_name=_('Level'), 
                null=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey('self', verbose_name=_('Parent Office'),
                null=True, on_delete=models.SET_NULL)
    
    _error_messages = {
        'root-has-parent': _("Business Office at Level-1 cannot have parent."),
        'parent-child-same-level': _("Parent and child Business Offices cannot "
                                     "be at the same Business Level."),
    }
    
    class Meta:
        db_table = 'business_office'
        ordering = ['level', 'name']
    
    def to_dict(self, minimal=True):
        return dict(id=self.id,
            code=self.code, name=self.name, email=self.email, phone=self.phone,
            website=self.website,  addr_street=self.addr_street,
            addr_town=self.addr_town, postal_code=self.postal_code,
            addr_raw=self.addr_raw, 
            addr_state=(self.addr_state.id if self.addr_state else 0),
            level=self.level.code if self.level else '',
            parent=self.parent.code if self.parent else '',
            date_created=self.date_created.strftime('%Y-%m-%d'), 
            last_updated=self.last_updated.strftime('%Y-%m-%d')
        )
    
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


class ApiServiceInfo(TimeStampedModel):
    """Maintains a registry of accessible API Services."""
    
    key = models.CharField(_("Service Key"), max_length=30, primary_key=True)
    api_root = models.URLField(_("API Root"), max_length=100, unique=True)
    api_token = models.CharField(_("API Token"), max_length=100, blank=True)
    
    def __str__(self):
        return "Service Key: {}".format(self.key)
    
    class Meta:
        db_table = 'apiservice_info'


#: ==+: document models

class StatsMixin(object):
    key = fields.StringField(required=True)
    count = fields.IntField(default=0)
    dup_cin = fields.IntField(default=0)
    dup_rseq = fields.IntField(default=0)
    dup_acct_no = fields.IntField(default=0)
    acct_new = fields.IntField(default=0)
    acct_existing = fields.IntField(default=0)
    acct_nosupply = fields.IntField(default=0)
    acct_ytbd = fields.IntField(default=0)
    meter_none = fields.IntField(default=0)
    meter_ppm = fields.IntField(default=0)
    meter_analogue = fields.IntField(default=0)


class Stats(Document, StatsMixin):
    meta = {
        'collection': 'stats_xf',
    }


class StatsBatch(Document, StatsMixin):
    date = fields.DateTimeField(required=True, unique_with='key')
    meta = {
        'collection': 'stats_bt',
        'ordering': ['key', '-date']
    }

