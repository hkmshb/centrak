from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from mongoengine import Document, EmbeddedDocument, fields



class TimeStampedDocument(Document):
    date_created = fields.DateTimeField()
    last_updated = fields.DateTimeField(default=datetime.now())
    
    meta = {
        'abstract': True
    }


#+----------------------------------------------------------------------------+
#: Network Asset Models
#+----------------------------------------------------------------------------+

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
    source = fields.ReferenceField('PowerLine', null=True)
    
    def __str__(self):
        return self.name
    
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
    
    HVOLTH, HVOLTL, MVOLTH, MVOLTL, LVOLT = range(1, 6)
    VOLT_CHOICES = (
        (HVOLTH, '330KV'), (HVOLTL, '132KV'),
        (MVOLTH,  '33KV'), (MVOLTL, '11KV'),
        (LVOLT, '0.415KV'),
    )
    
    object_id = fields.IntField(unique=True)
    code  = fields.StringField(max_length=2, required=True)
    icode = fields.StringField(max_length=20, required=False)
    name  = fields.StringField(max_length=50, required=True, unique=True)
    type  = fields.StringField(max_length=1, required=True, choices=TYPE_CHOICES)
    voltage = fields.IntField(required=True, choices=VOLT_CHOICES)
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

