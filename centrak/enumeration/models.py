from datetime import datetime
from collections import OrderedDict
from django.utils.translation import ugettext_lazy as _
from mongoengine import Document, fields



class TimeStampedDocument(Document):
    date_created = fields.DateTimeField()
    last_updated = fields.DateTimeField(default=datetime.now())
    
    meta = {
        'abstract': True
    }


#+----------------------------------------------------------------------------+
#: Network Asset Models
#+----------------------------------------------------------------------------+


class Volt:
    HVOLTH, HVOLTL, MVOLTH, MVOLTL, LVOLT = range(1, 6)
    _Text = OrderedDict({
        HVOLTH:'330KV', HVOLTL:'132KV', MVOLTH:'33KV', MVOLTL:'11KV',
        LVOLT:'0.415KV'})
    
    ALL_CHOICES = (
        (HVOLTH, _Text[HVOLTH]), (HVOLTL, _Text[HVOLTH]),
        (MVOLTH, _Text[MVOLTH]), (MVOLTL, _Text[MVOLTL]),
        (LVOLT, _Text[LVOLT]))
    
    LINE_CHOICES = ((MVOLTH, _Text[MVOLTH]), (MVOLTL, _Text[MVOLTL]))
    
    class Ratio:
        HVOLTH_HVOLTL, HVOLTL_MVOLTH, HVOLTL_MVOLTL = range(1, 4)
        MVOLTH_MVOLTL, MVOLTH_LVOLT, MVOLTL_LVOLT = range(4, 7)
        
        _Text = OrderedDict({
            HVOLTH_HVOLTL:'330/132KV', HVOLTL_MVOLTH:'132/33KV',
            HVOLTL_MVOLTL:'132/11KV', MVOLTH_MVOLTL:'33/11KV',
            MVOLTH_LVOLT:'33/0.415KV', MVOLTL_LVOLT:'11/0.415KV'})
        
        ALL_CHOICES = (
            (HVOLTH_HVOLTL, _Text[HVOLTH_HVOLTL]), (HVOLTL_MVOLTH, _Text[HVOLTL_MVOLTH]),
            (HVOLTL_MVOLTL, _Text[HVOLTL_MVOLTL]), (MVOLTH_MVOLTL, _Text[MVOLTH_MVOLTL]),
            (MVOLTH_LVOLT, _Text[MVOLTH_LVOLT]), (MVOLTL_LVOLT, _Text[MVOLTL_LVOLT]))
        
        PS_CHOICES = (
            (HVOLTH_HVOLTL, _Text[HVOLTH_HVOLTL]), (HVOLTL_MVOLTH, _Text[HVOLTL_MVOLTH]),
            (HVOLTL_MVOLTL, _Text[HVOLTL_MVOLTL]), (MVOLTH_MVOLTL, _Text[MVOLTH_MVOLTL]))
        
        DS_CHOICES = (
            (MVOLTH_LVOLT, _Text[MVOLTH_LVOLT]), (MVOLTL_LVOLT, _Text[MVOLTL_LVOLT]))


class PowerStation(TimeStampedDocument):
    """Represents a power station within an electricity distribution network."""
    
    TRANSMISSION = 'T'
    INJECTION    = 'I'
    
    STATION_CHOICES = (
        (TRANSMISSION, 'Transmission'),
        (INJECTION,    'Injection'),
    )
    
    object_id = fields.IntField(unique=True)
    code = fields.StringField(max_length=4, required=True)
    icode = fields.StringField(max_length=20, null=True, required=False) 
    name = fields.StringField(max_length=50, required=True, unique=True)
    type = fields.StringField(max_length=1, required=True, 
                choices=STATION_CHOICES)
    voltage_ratio = fields.IntField(required=True, choices=Volt.Ratio.ALL_CHOICES)
    source = fields.ReferenceField('PowerLine', null=True)
    
    meta = {
        'collection': 'stations',
    }
    
    def __str__(self):
        return '{} {}'.format(Volt.Ratio._Text[self.voltage_ratio], self.name)
    
    def tagcode(self):
        return self.code 


class PowerLine(TimeStampedDocument):
    """Represents a power line within an electricity distribution network.
    
    Hint: `icode` (internal code) is the internal code used within the Utility 
    company if any whereas `code` is the code which conforms with the industry
    regulatory body prescribed format.
    """
    
    FEEDER = 'F'
    UPRISER = 'U'
    TYPE_CHOICES = (
        (FEEDER,  'Feeder'),
        (UPRISER, 'Upriser'),
    )
    
    object_id = fields.IntField(unique=True)
    code  = fields.StringField(max_length=2, required=True)
    icode = fields.StringField(max_length=20, required=False)
    name  = fields.StringField(max_length=50, required=True, unique=True)
    type  = fields.StringField(max_length=1, required=True, choices=TYPE_CHOICES)
    voltage = fields.IntField(required=True, choices=Volt.LINE_CHOICES)
    public = fields.BooleanField(default=True)
    source = fields.ReferenceField(PowerStation)
    
    def tagcode(self):
        # nerc: combination of source station and assigned code
        pass



#+----------------------------------------------------------------------------+
#: Enum. Resx. Models
#+----------------------------------------------------------------------------+


class XForm(TimeStampedDocument):
    """Represents an XForm used on the Survey platform."""
    
    TYPE_CAPTURE = 'C'
    TYPE_UPDATE  = 'U'
    
    TYPE_CHOICES = (
        (TYPE_CAPTURE, _("Capture XForm")),
        (TYPE_UPDATE,  _("Update XForm")),
    ) 
    
    object_id = fields.IntField(unique=True, required=True)
    id_string = fields.StringField(max_length=30, unique=True, required=True)
    title = fields.StringField(max_length=50, unique=True, required=True)
    type = fields.StringField(max_length=1, choices=TYPE_CHOICES)
    description = fields.StringField(required=False)
    active = fields.BooleanField(default=False)
    url = fields.URLField(max_length=100, required=True)
    synced_by = fields.StringField(max_length=50, required=False)
    last_synced = fields.DateTimeField()
    date_imported = fields.DateTimeField()
    
    meta = {
        'collection': 'xforms',
        'ordering': ['object_id'],
    }
    
    def __str__(self):
        return self.title or self.id_string


class Project(TimeStampedDocument):
    """Represents an endeavour to enumerate customers on a high tension (HT)
    PowerLine (Feeder)."""
    
    STATUS_IN_VIEW     = 1
    STATUS_IN_PROGRESS = 2
    STATUS_CONCLUDED   = 3
    STATUS_REVISITED   = 4
    
    STATUS_CHOICES = (
        (STATUS_IN_VIEW, 'In View'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_CONCLUDED, 'Concluded'),
        (STATUS_REVISITED, 'Revisited'),
    )
    
    code = fields.StringField(unique=True, required=True)
    name = fields.StringField(max_length=50, unique=True, required=True)
    description = fields.StringField(required=False, null=True)
    status = fields.IntField(required=True, default=STATUS_IN_VIEW,
                choices=STATUS_CHOICES)
    active = fields.BooleanField(default=False)
    date_started = fields.DateTimeField(null=True)
    date_ended = fields.DateTimeField(null=True)
    
    meta = {
        'collection': 'projects',
        'ordering': ['object_id'],
    }
    
    def __str__(self):
        return "{} :: [Project {}]".format(
            self.title, self.get_status_display()
        )

