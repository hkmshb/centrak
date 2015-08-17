from django.db import models



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
        return "%s (by %s)" % (self.name, self.provider)


class Device(models.Model):
    PHONE   = 'P'
    TABLET  = 'T'
    FORM_FACTOR_CHOICES = (
        (PHONE,  'Phone'),
        (TABLET, 'Tablet')
    )
    
    brand = models.ForeignKey(Manufacturer)
    model = models.CharField(max_length=50)
    mobile_os   = models.ForeignKey(MobileOS)
    os_version  = models.CharField(max_length=25)
    form_factor = models.CharField(max_length=1, 
                    choices=FORM_FACTOR_CHOICES,
                    default=PHONE)
    serialno = models.CharField(max_length=25, blank=True)
    
    class Meta:
        db_table = 'enum_device'
    
    
class DeviceIMEI(models.Model):
    device = models.ForeignKey(Device)
    imei = models.CharField(max_length=25, unique=True)
    
    class Meta:
        db_table = 'enum_device_imei'
    
    def __str__(self):
        return "imei=%s" % self.imei

