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
    date_created = fields.DateTimeField(default=datetime.now())
    last_updated = fields.DateTimeField()


class TimestampedDocument(Document, TimestampedMixin):
    meta = {
        'abstract': True
    }


class AddressMixin(object):
    """
    A mixin which defines address fields.
    """
    addr_raw      = fields.StringField(max_length=200, blank=True)
    addr_street   = fields.StringField(max_length=100, blank=True)
    addr_town     = fields.StringField(max_length=20, blank=True)
    addr_state    = fields.StringField(blank=True)
    postal_code   = fields.StringField(max_length=10, blank=True)
    addr_landmark = fields.StringField(max_length=50, blank=True)    


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

    acct_no     = fields.StringField(max_length=16)
    book_code   = fields.StringField(max_length=8)
    title       = fields.StringField(max_length=12, choices=constants.Title.CHOICES)
    cust_name   = fields.StringField(max_length=100, required=True)
    cust_mobile = fields.StringField(max_length=15)
    cust_email  = fields.EmailField(max_length=100)
    tariff      = fields.StringField(max_length=3, choices=constants.Tariff.CHOICES)
    meter_no    = fields.StringField(max_length=20)
    acct_status = fields.StringField(max_length=15, choices=STATUS_CHOICES)
    service_addr = fields.StringField(max_length=150)


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
    
    object_id = fields.IntField(unique=True, required=True)
    id_string = fields.StringField(max_length=30, unique=True, required=True)
    title = fields.StringField(max_length=50, unique=True, required=True)
    description = fields.StringField(required=False)
    type = fields.StringField(max_length=1, choices=TYPE_CHOICES)
    url  = fields.URLField(max_length=100, required=True)
    is_active = fields.BooleanField(default=False)
    synced_by = fields.StringField(max_length=50, required=False)
    last_synced = fields.DateTimeField()
    date_imported = fields.DateTimeField()
    
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
    
    medium = fields.StringField(max_length=1, null=False, choices=MEDIUM_CHOICES)

    # date_created is used as capture date
    date_digitized = fields.DateTimeField()

    # organization
    region_name  = fields.StringField(max_length=20, blank=False)
    csp_code     = fields.StringField(max_length=20, blank=True)
    csp_name     = fields.StringField(max_length=50, blank=False)

    # staff names
    user_email      = fields.EmailField(max_length=50, required=True)
    csp_supr_name   = fields.StringField(max_length=50)
    tsp_engr_name   = fields.StringField(max_length=50)
    sales_repr_name = fields.StringField(max_length=50)

    # energy-source
    feeder_code  = fields.StringField(max_length=50, blank=True)
    feeder_name  = fields.StringField(max_length=50, blank=False)
    station_code = fields.StringField(max_length=20, blank=True)
    station_name = fields.StringField(max_length=50, blank=False)
    upriser_no   = fields.IntField(min_value=1, max_value=8)
    pole_no      = fields.IntField(min_value=1)
    wire_no      = fields.IntField(min_value=1)

    # address info
    addr_landmark = fields.StringField(max_length=50)
    addr_no       = fields.StringField(max_length=20)
    addr_street   = fields.StringField(max_length=50)
    addr_town     = fields.StringField(max_length=20)
    addr_state    = fields.StringField(max_length=20)

    meta = {
        'collection': 'captures',
        'ordering': ['medium', 'date_created'],
    }
    
    def __str__(self):
        return ("%(region_name)s %(acct_info)s %(cust_name)s" % {
            'region_name': self.region_name,
            'acct_info': self.acct_no or self.book_code,
            'cust_name': self.cust_name
        })
