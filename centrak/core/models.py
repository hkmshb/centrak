import uuid
from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models

from ezaddress.models import Addressable, GPSLocatable
from .exceptions import InvalidOperationError



#*----------------------------------------------------------------------------+
#| Abstract Core Models
#+----------------------------------------------------------------------------+
class TimeStampedModel(models.Model):
    """
    Abstract base model with fields for tracking object creation and last
    update dates.
    """
    date_created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True, null=True)

    class Meta:
        abstract = True


#*----------------------------------------------------------------------------+
#| UserProfile and other User related models.
#+----------------------------------------------------------------------------+
class UserProfile(models.Model):
    """
    Extension of the User model.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    phone   = models.CharField(_('Phone'), max_length=20, blank=True)
    location = models.ForeignKey('BusinessOffice', null=True)

    @property
    def full_location(self):
        value, loc = None, self.location
        if loc:
            value = loc.name
            if loc.level.code == BusinessLevel.LEVEL2 and loc.parent:
                value = "%s, %s" % (loc.parent.name, value)
        return value
    
    def get_absolute_url(self):
        return reverse('admin-user-info', args=[self.user.id])

    def __str__(self):
        if self.user:
            return self.user.first_name
        return ""


class UserSettings(models.Model):
    """
    Represents user application settings.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='settings')
    page_size = models.PositiveSmallIntegerField(_('General Page Size'), 
                    default=settings.CENTRAK_DEFAULT_PAGE_SIZE)
    capture_page_size = models.PositiveIntegerField(_('Capture Page Size'),
                    default=settings.CENTRAK_CAPTURE_PAGE_SIZE)

#*----------------------------------------------------------------------------+
#| ApiServiceInfo + Notifications
#+----------------------------------------------------------------------------+
class ApiServiceInfo(TimeStampedModel):
    """
    Maintains a list of accessible API Services.
    """
    key = models.CharField(_('Service Key'), max_length=20, primary_key=True)
    title = models.CharField(_('Service Title'), max_length=50, unique=True)
    description = models.TextField(_('Service Description'), blank=True)
    api_root  = models.URLField(_('API Root'), max_length=100, unique=True)
    api_auth  = models.URLField(_('API Auth'), max_length=100, blank=True)
    api_extra = models.URLField(_('API Extra'), max_length=100, blank=True)
    api_token = models.CharField(_('API Token'), max_length=100, blank=True)
    is_active = models.BooleanField(_('Is Active'), default=False)

    def __str__(self):
        return "Service: [{}], {}".format(self.key, self.title)
    
    class Meta:
        db_table = 'apiservice_info'
    
    def get_absolute_url(self):
        return reverse('admin-apiservice-info', args=[self.key])


class Notification(TimeStampedModel):
    """Maintains a list of long lived notification messages.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    message = models.TextField(_('Message'))
    read = models.BooleanField(_('Read'), default=False)
    task_id = models.CharField(_('Task Id'), max_length=100, blank=True)
    task_status = models.CharField(_('Task Status'), max_length=32, blank=True)

    @property
    def is_task(self):
        return self.task_id and self.task_id.strip() != ''

    def __str__(self):
        return "Notification: [task={}, read={}] {}".format(
            'Y' if self.is_task else 'N', 'Y' if self.read else 'N',
            self.message[:70] + ('...' if len(self.message) > 20 else '')
        )


#*----------------------------------------------------------------------------+
#| BusinessEntity Models
#+----------------------------------------------------------------------------+
class BusinessEntity(TimeStampedModel, Addressable, GPSLocatable):
    """
    Abstract base class which represents a Business entity.
    """
    uuid    = models.UUIDField(_('UUID'), default=uuid.uuid4, editable=False)
    name    = models.CharField(_('Name'), max_length=40, unique=True)
    short_name = models.CharField(_('Short Name'), max_length=20, unique=True)
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

    code = models.CharField(_('Code'), max_length=12, unique=True)
    level = models.ForeignKey(BusinessLevel, verbose_name=_('Level'), 
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
        permissions = (
            ('can_manage_region', "Can add, change and delete Level1 objects"),
            ('can_import', "Can import LEVEL2 objects."),
            ('can_export', "Can export LEVEL2 objects.")
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
            
            if self.level.code == BusinessLevel.LEVEL2:
                if self.category in (None, ""):
                    message = self._error_messages['category-required']
                    raise ValidationError(message)
            else:
                if self.category not in (None, ""):
                    message = self._error_messages['category-not-required']
                    raise ValidationError(message)
    
    def get_absolute_url(self):
        if self.level.code == BusinessLevel.LEVEL1:
            return reverse('admin-region-info', args=[self.code])
        elif self.level.code == BusinessLevel.LEVEL2:
            return reverse('admin-office-info', args=[self.code])
        return None


#*----------------------------------------------------------------------------+
#| Network Models
#+----------------------------------------------------------------------------+
class Voltage:
    """
    Defines voltage levels within an electricity distribution network.
    """
    HVOLTH, HVOLTL, MVOLTH, MVOLTL, LVOLT = range(5, 0, -1)

    _TEXT = OrderedDict({
        HVOLTH: '330KV', HVOLTL: '132KV', MVOLTH: '33KV', MVOLTL: '11KV',
        LVOLT: '0.415KV' })

    ALL_CHOICES = (
        (HVOLTH, _TEXT[HVOLTH]), (HVOLTL, _TEXT[HVOLTL]),
        (MVOLTH, _TEXT[MVOLTH]), (MVOLTL, _TEXT[MVOLTL]),
        (LVOLT,  _TEXT[LVOLT]))
    
    class Ratio:
        """
        Defines voltage ratios within an electricity distribution network.
        """
        HVOLTH_HVOLTL, HVOLTL_MVOLTH, HVOLTL_MVOLTL = range(6, 3, -1)
        MVOLTH_MVOLTL, MVOLTH_LVOLT, MVOLTL_LVOLT = range(3, 0, -1)

        _TEXT = OrderedDict({
            HVOLTH_HVOLTL: '330/132KV', HVOLTL_MVOLTH: '132/33KV',
            HVOLTL_MVOLTL: '132/11KV',  MVOLTH_MVOLTL: '33/11KV',
            MVOLTH_LVOLT: '33/0.415KV', MVOLTL_LVOLT: '11/0.415KV'
        })

        ALL_CHOICES = (
            (HVOLTH_HVOLTL, _TEXT[HVOLTH_HVOLTL]), (HVOLTL_MVOLTH, _TEXT[HVOLTL_MVOLTH]),
            (HVOLTL_MVOLTL, _TEXT[HVOLTL_MVOLTL]), (MVOLTH_MVOLTL, _TEXT[MVOLTH_MVOLTL]),
            (MVOLTH_LVOLT, _TEXT[MVOLTH_LVOLT]),  (MVOLTL_LVOLT, _TEXT[MVOLTL_LVOLT]))


class NetworkEntity(TimeStampedModel):
    """
    Abstract base class for network model objects.
    """
    uuid  = models.UUIDField(_('UUID'), default=uuid.uuid4, editable=False)
    code  = models.CharField(_('Code'), max_length=20, unique=True)
    altcode = models.CharField(_('Alternative Code'), max_length=20, 
                unique=True, blank=True)
    is_public = models.BooleanField(_('Is Public'), default=True)
    last_synced = models.DateTimeField(_('Last Synced'), null=True)
    date_commissioned = models.DateField(null=True)
    region = models.ForeignKey('BusinessOffice', blank=True, null=True)
    
    class Meta:
        abstract = True
        permissions = (
            ('can_sync_data', "Can pull in data from external service"),
            ('can_export', "Can export entity data")
        )


class Station(NetworkEntity, Addressable, GPSLocatable):
    """
    Represents a power station within an electricity distribution network.
    """
    TRANSMISSION = 1
    INJECTION    = 2
    DISTRIBUTION = 3
    STATION_CHOICES = (
        (TRANSMISSION, 'Transmission'),
        (INJECTION,    'Injection'),
        (DISTRIBUTION, 'Distribution')
    )
    name = models.CharField(_('Name'), max_length=100)
    type = models.PositiveSmallIntegerField(_('Type'), choices=STATION_CHOICES)
    voltage_ratio = models.PositiveSmallIntegerField(_('Voltage Ratio'), 
                        choices=Voltage.Ratio.ALL_CHOICES)
    source_powerline = models.ForeignKey('Powerline', blank=True, null=True)
    
    class Meta:
        unique_together = ('name', 'type')


class Powerline(NetworkEntity):
    """
    Represents a power line within an electricity distribution network.
    """
    FEEDER  = 1
    UPRISER = 2
    POWERLINE_CHOICES = (
        (FEEDER,  'Feeder'),
        (UPRISER, 'Upriser')
    )
    name = models.CharField(_('Name'), max_length=100)
    type = models.PositiveSmallIntegerField(_('Type'), choices=POWERLINE_CHOICES)
    voltage = models.PositiveSmallIntegerField(_('Voltage'), choices=Voltage.ALL_CHOICES)
    source_station = models.ForeignKey(Station, blank=True, null=True)
    line_length = models.IntegerField(_('Line Length'), blank=True, null=True)
    pole_count = models.IntegerField(_('Pole Count'), blank=True, null=True)
    
    class Meta:
        unique_together = ('name', 'type')
