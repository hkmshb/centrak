from django.db import models



class Manufacturer(models.Model):
    name = models.CharField(max_length=25, unique=True)
    
    class Meta:
        db_table = 'enum_manufacturer'
    
    def __str__(self):
        return self.name


class MobileOS(models.Model):
    name     = models.CharField(max_length=25, unique=True)
    provider = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'enum_mobileos'
    
    def __str__(self):
        return '%s (by %s)' % (self.name, self.provider)

    