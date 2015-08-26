from django.db import models
from django.core.exceptions import ValidationError


# const error messages
UNIQUE_SERIALNO_ERROR  = "Serial # already exist."



class Manufacturer(models.Model):
    name = models.CharField(max_length=25, unique=True)
    
    class Meta:
        db_table = 'enum_manufacturer'
    
    def __str__(self):
        return self.name


class MobileOS(models.Model):
    name     = models.CharField(max_length=25, unique=True)
    provider = models.CharField(max_length=50, blank=True, default='')
    
    class Meta:
        db_table = 'enum_mobileos'
    
    def __str__(self):
        return self.name


class Device(models.Model):
    PHONE   = 'P'
    TABLET  = 'T'
    FORM_FACTOR_CHOICES = (
        (PHONE,  'Phone'),
        (TABLET, 'Tablet')
    )
    
    label = models.CharField(max_length=10, unique=True)
    brand = models.ForeignKey(Manufacturer)
    model = models.CharField(max_length=50, blank=True)
    mobile_os   = models.ForeignKey(MobileOS)
    os_version  = models.CharField(max_length=25, blank=True)
    form_factor = models.CharField(max_length=1, 
                    choices=FORM_FACTOR_CHOICES,
                    default=PHONE)
    serialno = models.CharField(max_length=25, blank=True)
    notes    = models.TextField(blank=True)
    
    class Meta:
        db_table = 'enum_device'
    
    def validate_unique(self, exclude=None):
        super(Device, self).validate_unique(exclude=exclude)
        serialno = (self.serialno or '')
        if serialno and Device.objects.filter(serialno=serialno).exists():
            raise ValidationError({'serialno': UNIQUE_SERIALNO_ERROR}, code='unique')


class DeviceIMEI(models.Model):
    device = models.ForeignKey(Device)
    imei = models.CharField(max_length=25, unique=True)
    
    class Meta:
        db_table = 'enum_device_imei'
    
    def __str__(self):
        return "imei=%s" % self.imei

