from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from mongoengine import Document, fields



class TimeStampedDocument(Document):
    date_created = fields.DateTimeField()
    last_updated = fields.DateTimeField(default=datetime.now())
    
    meta = {
        'abstract': True
    }


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

