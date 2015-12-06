from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models

from core.models import BusinessOffice



# const error messages
UNIQUE_SERIALNO_ERROR  = "Serial # already exist."


class IsActiveManagerMixin:
    """A Manager mixin for models with the 'is_active' field. Holds generic
    query methods returning results based on state of this field.
    """
    
    def all(self, include_inactive=False):
        q = (self.get_queryset().filter()
                if include_inactive else
                    self.get_queryset().filter(is_active=True))
        return q


class IsActiveManager(IsActiveManagerMixin, models.Manager):
    """A Manager that can be directly sub-classed or used directly for models
    that need to manage query methods relying on the 'is_active' field in a
    general way.
    """
    pass


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
    
    def as_choices(self, include_none=False):
        if include_none: yield ('0', 'None')
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


class PersonManager(IsActiveManagerMixin, models.Manager):
    
    def unassigned(self):
        # get people that belong to teams
        qs_team = Team.objects.filter(is_active=True, members__isnull=False)
        mem_ids = [m['members'] for m in qs_team.values('members')]
        
        # people that are supervisors
        qs_group = Group.objects.filter(is_active=True, supervisor__isnull=False)
        supvr_ids = [s['supervisor'] for s in qs_group.values('supervisor')]
        
        return Person.objects.exclude(id__in=(mem_ids + supvr_ids))
    
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


class TeamManager(IsActiveManagerMixin, models.Manager):
    
    def unassigned(self):
        # get teams that belong to groups already
        qs_group = Group.objects.filter(is_active=True, teams__isnull=False)
        team_ids = [t['teams'] for t in qs_group.values('teams')]
        
        return Team.objects.exclude(id__in=team_ids)
    
    def unassigned_as_choices(self):
        for team in self.unassigned():
            yield (team.id, '%s: %s' % (team.code, team.name))


class Team(NamedEntityBase):
    code = models.CharField(max_length=20, unique=True)
    devices = models.ManyToManyField(Device)
    members = models.ManyToManyField(Person, through='TeamMembership')
    
    objects = TeamManager()
    
    class Meta:
        db_table = 'enum_team'
    
    def get_absolute_url(self):
        args = [self.id]
        return reverse('team-view', args=args)
    
    @staticmethod
    def get_devices_part_label():
        return 'devices'
    
    @staticmethod
    def is_devices_part_label(label):
        return label == 'devices'
    
    @staticmethod
    def part_labels():
        return ['members', 'devices']


class TeamMembership(models.Model):
    team    = models.ForeignKey(Team, on_delete=models.PROTECT)
    person  = models.ForeignKey(Person, on_delete=models.PROTECT)
    device  = models.ForeignKey(Device, null=True, blank=True, on_delete=models.PROTECT)
    role    = models.CharField(max_length=2, 
                choices=MemberRole.ROLE_CHOICES,
                default=MemberRole.MEMBER)
    date_joined = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'enum_team_membership'
    
    def clean(self):
        # enumerators must be assigned a device
        if self.role == MemberRole.ENUMERATOR and not self.device:
            raise ValidationError('Enumerators must be assigned a device.')
        
        # don't allow non enumerators to be assigned a device
        if self.device and self.role != MemberRole.ENUMERATOR:
            raise ValidationError('Only enumerators can be assigned a device.')
        
        # don't allow single device to be assigned to multiple members
        if self.device:
            memberships = TeamMembership.objects.exclude(team=self.team, 
                            device=self.device, person=self.person)
            in_use = [m.device for m in memberships if m.device == self.device]
            if in_use:
                message = 'Cannot assign a device to more than on enumerator.'
                raise ValidationError(message)
                

class Group(NamedEntityBase):
    supervisor = models.ForeignKey(Person, on_delete=models.PROTECT)
    note       = models.TextField(blank=True)
    teams      = models.ManyToManyField(Team)

    objects = IsActiveManager()
    
    class Meta:
        db_table = 'enum_group'

    def clean(self):
        # ensure group is assigned a supervisor
        if not self.supervisor:
            raise ValidationError('Group must be assigned a supervisor.')
        
        # ensure supervisor isn't a member of any team
        team_membership = TeamMembership.objects.filter(team__is_active=True,
                            person=self.supervisor)
        if team_membership:
            message = 'The specified person already belongs to an active team.'
            raise ValidationError(message)
        
        # ensure single person cannot supervise multiple groups
        supervised_groups = Group.objects.filter(is_active=True, 
                                supervisor=self.supervisor)
        if supervised_groups:
            message = 'The specified person already supervises an active group.'
            raise ValidationError(message)
        
