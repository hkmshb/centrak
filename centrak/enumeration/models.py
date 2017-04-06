from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.db import models

from mongoengine import Document, fields

from ezaddress.models import Addressable
from core.models import TimeStampedModel
from . import constants



#+----------------------------------------------------------------------------+
#: Relational Models
#+----------------------------------------------------------------------------+
class Account(TimeStampedModel):
    """
    Represents KEDCO Customer Accounts to be validated.
    """
    # account status options
    ACTIVE   = 'A'
    INACTIVE = 'I'
    STATUS_CHOICES = (
        (ACTIVE, "Active"), (INACTIVE, "Inactive")
    )

    # standard fields
    acct_no = models.CharField(_("Account No."), max_length=16, blank=False, 
                    unique=True)
    book_code   = models.CharField(_("Book Code"), max_length=8, blank=False)
    cust_name   = models.CharField(_("Customer Name"), max_length=100, blank=False)
    cust_mobile = models.CharField(_("Mobile"), max_length=20, blank=True, null=True)
    acct_status = models.CharField(_("Status"), max_length=3, blank=True, 
                    null=True, choices=STATUS_CHOICES)
    tariff    = models.CharField(_("Tariff"), max_length=5, choices=constants.Tariff.CHOICES)
    meter_no  = models.CharField(_("Meter No."), max_length=20, blank=True, null=True) 
    service_addr = models.CharField(_("Service Address"), max_length=150, null=True, blank=True)

    class Meta:
        db_table = 'enum_account'
    
    def __str__(self):
        return ("%(acct_info)s; %(cust_name)s; %(tariff)s; %(acct_status)s" % {
            'acct_info': self.acct_no or self.book_code, 'tariff': self.tariff,
            'cust_name': self.cust_name, 'acct_status': self.acct_status             
        })


#+============================================================================+
#: NoSQL Document Models    
#+----------------------------------------------------------------------------+    
class TimestampedMixin(object):
    date_created = fields.DateTimeField(default=datetime.now(), verbose_name='Date Created')
    last_updated = fields.DateTimeField(verbose_name='Last Updated')


class TimestampedDocument(Document, TimestampedMixin):
    meta = {
        'abstract': True
    }


class AddressMixin(object):
    """
    A mixin which defines address fields.
    """
    addr_raw      = fields.StringField(max_length=200, blank=True, verbose_name='Raw Address')
    addr_street   = fields.StringField(max_length=100, blank=True, verbose_name='Address Street')
    addr_town     = fields.StringField(max_length=20, blank=True, verbose_name='Address Town')
    addr_state    = fields.StringField(blank=True, verbose_name='Address State')
    postal_code   = fields.StringField(max_length=10, blank=True, verbose_name='Postal Code')
    addr_landmark = fields.StringField(max_length=50, blank=True, verbose_name='Closest Landmark')    


class AccountMixin(object):
    """
    A mixin which defines account fields.
    """
    NEW       = 'new'
    EXISTING  = 'existing'
    NO_SUPPLY = 'no-supply'
    UNKNOWN   = 'unknown'
    STATUS_CHOICES = (
        (NEW,       _("New")),
        (EXISTING,  _("Existing")),
        (NO_SUPPLY, _("No Supply")),
        (UNKNOWN,   _("Unknown"))
    )

    acct_no     = fields.StringField(max_length=16, verbose_name='Account No')
    book_code   = fields.StringField(max_length=8, verbose_name='Book Code')
    title       = fields.StringField(max_length=12, choices=constants.Title.CHOICES,
                        verbose_name='Title')
    cust_name   = fields.StringField(max_length=100, required=True, 
                        verbose_name='Customer Name')
    cust_mobile = fields.StringField(max_length=15, verbose_name='Customer Mobile')
    cust_email  = fields.EmailField(max_length=100, verbose_name='Customer Email')
    tariff      = fields.StringField(max_length=3, choices=constants.Tariff.CHOICES, 
                        verbose_name='Tariff')
    meter_no    = fields.StringField(max_length=20, verbose_name='Meter No')
    acct_status = fields.StringField(max_length=15, choices=STATUS_CHOICES, 
                        verbose_name='Account Status')
    service_addr = fields.StringField(max_length=150, verbose_name='Service Address')


#+----------------------------------------------------------------------------+
#: Enumeration Data Organisation Models
#+----------------------------------------------------------------------------+
class XForm(TimestampedDocument):
    """
    Represents an XForm used on the Survey platform.
    """
    TYPE_CAPTURE = 'C'
    TYPE_UPDATE  = 'U'
    TYPE_CHOICES = (
        (TYPE_CAPTURE, _('Capture XForm')),
        (TYPE_UPDATE,  _('Update XForm')),
    )
    
    object_id = fields.IntField(unique=True, required=True, verbose_name='Object Id')
    id_string = fields.StringField(max_length=30, unique=True, required=True, 
                    verbose_name='Id String')
    title = fields.StringField(max_length=50, unique=True, required=True, 
                    verbose_name='Title')
    description = fields.StringField(required=False, verbose_name='Description')
    type = fields.StringField(max_length=1, choices=TYPE_CHOICES, verbose_name='Type')
    url  = fields.URLField(max_length=100, required=True, verbose_name='Url')
    is_active = fields.BooleanField(default=False, verbose_name='Is Active')
    synced_by = fields.StringField(max_length=50, required=False, verbose_name='Synced By')
    last_synced = fields.DateTimeField(verbose_name='Last Synced')
    date_imported = fields.DateTimeField(verbose_name='Date Imported')
    
    meta = {
        'collection': 'xforms',
        'ordering': ['object_id'],
    }
    
    def __str__(self):
        return self.title or self.id_string


class Capture(TimestampedDocument, AccountMixin, AddressMixin):
    """
    Represents captures made during the enumeration exercise.
    """
    MEDIUM_PAPER  = 'P'
    MEDIUM_MOBILE = 'M'
    MEDIUM_CHOICES = (
        (MEDIUM_PAPER,  _("Paper-Based Capture")),
        (MEDIUM_MOBILE, _("Mobile-Based Capture"))
    )
    
    medium = fields.StringField(max_length=1, null=False, choices=MEDIUM_CHOICES, 
                    verbose_name='Medium')

    # date_created is used as capture date
    date_digitized = fields.DateTimeField(verbose_name='Date Digitized')

    # organization
    region_code = fields.StringField(max_length=12, blank=False, verbose_name='Region Code')
    region_name = fields.StringField(max_length=50, blank=False, verbose_name='Region Name')
    csp_code    = fields.StringField(max_length=20, blank=True, verbose_name='CSP Code')
    csp_name    = fields.StringField(max_length=50, blank=False, verbose_name='CSP Name')

    # staff names
    user_email      = fields.EmailField(max_length=50, required=True, verbose_name='User Email')
    csp_supr_name   = fields.StringField(max_length=50, verbose_name='CSP Supervisor')
    tsp_engr_name   = fields.StringField(max_length=50, verbose_name='TSP Engineer')
    sales_repr_name = fields.StringField(max_length=50, verbose_name='Sales Representative')

    # energy-source
    feeder_code  = fields.StringField(max_length=50, blank=True, verbose_name='Feeder Code')
    feeder_name  = fields.StringField(max_length=50, blank=False, verbose_name='Feeder')
    station_code = fields.StringField(max_length=20, blank=True, verbose_name='Station Code')
    station_name = fields.StringField(max_length=50, blank=False, verbose_name='Station')
    upriser_no   = fields.IntField(min_value=1, max_value=8, verbose_name='Upriser No')
    pole_no      = fields.IntField(min_value=1, verbose_name='Pole No')
    wire_no      = fields.IntField(min_value=1, verbose_name='Wire No')

    # address info
    addr_landmark = fields.StringField(max_length=50, verbose_name='Closest Landmark')
    addr_no       = fields.StringField(max_length=20, verbose_name='Address No')
    addr_street   = fields.StringField(max_length=50, verbose_name='Address Street')
    addr_town     = fields.StringField(max_length=20, verbose_name='Address Town')
    addr_state    = fields.StringField(max_length=20, verbose_name='Address State')

    meta = {
        'collection': 'captures',
        'ordering': ['medium', 'date_created'],
    }
    
    def __str__(self):
        return ("%(region_code)s %(region_name)s %(acct_info)s %(cust_name)s" % {
            'region_code': self.region_code, 
            'region_name': self.region_name,
            'acct_info': self.acct_no or self.book_code,
            'cust_name': self.cust_name
        })
