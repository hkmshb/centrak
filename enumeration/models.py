from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models

from core.models import BusinessOffice



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


class DeviceManager(models.Manager):
    
    def unassigned(self):
        qs  = Team.objects.filter(is_active=True, devices__isnull=False)
        ids = [d['devices'] for d in qs.values('devices')]
        return Device.objects.exclude(id__in = ids)
    
    def as_choices(self):
        for device in self.all():
            yield (device.pk, device.label)
    
    def unassigned_as_choices(self):
        for device in self.unassigned():
            yield (device.id, device.label)


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
    
    objects = DeviceManager()
    
    class Meta:
        db_table = 'enum_device'
    
    def validate_unique(self, exclude=None):
        super(Device, self).validate_unique(exclude=exclude)
        serialno = (self.serialno or '')
        if serialno and Device.objects.filter(serialno=serialno).exists():
            raise ValidationError({'serialno': UNIQUE_SERIALNO_ERROR}, code='unique')

    def __str__(self):
        return self.label


class DeviceIMEI(models.Model):
    device = models.ForeignKey(Device)
    imei = models.CharField(max_length=25, unique=True)
    
    class Meta:
        db_table = 'enum_device_imei'
    
    def __str__(self):
        return "imei=%s" % self.imei


class EntityBase(models.Model):
    is_active    = models.BooleanField(default=True)
    date_created = models.DateField(auto_now_add=True)
    
    class Meta:
        abstract = True


class NamedEntityBase(EntityBase):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        abstract = True


class PersonManager(models.Manager):
    
    def unassigned(self):
        qs = Team.objects.filter(is_active=True, members__isnull=False)
        ids = [m['members'] for m in qs.values('members')]
        return Person.objects.exclude(id__in=ids)
    
    def unassigned_as_choices(self):
        for person in self.unassigned():
            yield (person.id, person.fullname)


class Person(EntityBase):
    MALE   = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE,   'Male'),
        (FEMALE, 'Female')
    )
    
    FULL_STAFF         = 'FS'
    CONTRACT_STAFF     = 'CS'
    YOUTH_CORPER       = 'YC'
    INDUSTRIAL_TRAINEE = 'IT'
    STATUS_CHOICES = (
        (FULL_STAFF,         'Full Staff'),
        (CONTRACT_STAFF,     'Contract Staff'),
        (YOUTH_CORPER,       'Youth Corper'),
        (INDUSTRIAL_TRAINEE, 'Industrial Trainee')
    )
    
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    gender     = models.CharField(max_length=1, choices=GENDER_CHOICES, 
                    default=MALE)
    official_status = models.CharField(max_length=2, choices=STATUS_CHOICES, 
                    default=FULL_STAFF)
    location  = models.ForeignKey(BusinessOffice, on_delete=models.PROTECT)
    mobile    = models.CharField(max_length=20)
    mobile2   = models.CharField(max_length=20, blank=True)
    email     = models.EmailField(max_length=50)
    
    objects = PersonManager()
    
    class Meta:
        db_table = 'enum_person'
        unique_together = ('first_name', 'last_name')
    
    @property
    def fullname(self):
        return '%s %s' % (self.first_name, self.last_name)


class MemberRole:
    SUPERVISOR = 'SP'
    LEAD       = 'LD'
    SCOUT      = 'ST'
    ENUMERATOR = 'EN'
    MARKER     = 'MK'
    RECORDER   = 'RC'
    MEMBER     = 'MB'
    
    ROLE_CHOICES = (
        (SUPERVISOR, 'Supervisor'), (LEAD, 'Lead'),
        (SCOUT, 'Scout'), (ENUMERATOR, 'Enumerator'),
        (MARKER, 'Marker'), (RECORDER, 'Recorder'),
        (MEMBER, 'Member')
    )


# class MemberRoleManager(models.Manager):
# 
#     def as_choices(self):
#         for role in self.all():
#             yield (role.pk, role.name)
# 
#     
# class MemberRole(NamedEntityBase):
#     description = models.TextField(blank=True)
#      
#     objects = MemberRoleManager()
#      
#     class Meta:
#         db_table = 'enum_member_role'


class Team(NamedEntityBase):
    code = models.CharField(max_length=20, unique=True)
    devices = models.ManyToManyField(Device)
    members = models.ManyToManyField(Person, through='TeamMembership')
    
    class Meta:
        db_table = 'enum_team'


class TeamMembership(models.Model):
    team    = models.ForeignKey(Team, on_delete=models.PROTECT)
    person  = models.ForeignKey(Person, on_delete=models.PROTECT)
    device  = models.ForeignKey(Device, on_delete=models.PROTECT)
    role    = models.CharField(max_length=2, 
                choices=MemberRole.ROLE_CHOICES,
                default=MemberRole.MEMBER)
    date_joined = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'enum_team_membership'

