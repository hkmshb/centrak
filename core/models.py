from django.db import models
from django.core.exceptions import ValidationError



class State(models.Model):
    code    = models.CharField(max_length=2, primary_key=True)
    name    = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'state'

    def __str__(self):
        return self.name


class BusinessEntity(models.Model):
    name    = models.CharField(max_length=50, unique=True)
    email   = models.EmailField(max_length=50, blank=True)
    phone   = models.CharField(max_length=20, blank=True)
    url     = models.URLField(max_length=50, blank=True)
    street1 = models.CharField(max_length=50, blank=True)
    street2 = models.CharField(max_length=50, blank=True)
    city    = models.CharField(max_length=20)
    state   = models.ForeignKey(State, on_delete=models.PROTECT)
    note    = models.TextField(blank=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name


class Organization(BusinessEntity):

    class Meta:
        db_table = 'organization'

    def clean(self):
        """Ensure only a single record can be stored"""
        super(Organization, self).clean()
        count = Organization.objects.count()
        if count > 0 and self.id in (None, 0):
            message = 'Multiple records cannot be stored for Organization.'
            raise ValidationError(message)


class BusinessOffice(BusinessEntity):
    
    class Meta:
        db_table = 'business_office'

