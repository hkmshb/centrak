from django.utils.translation import ugettext_lazy as _
from django.db import models

from core.models import TimeStampedModel



class XForm(TimeStampedModel):
    """Represents an XForm used on the Surveys platform."""
    
    TYPE_CAPTURE = 'C'
    TYPE_UPDATE  = 'U'
    
    TYPE_CHOICES = (
        (TYPE_CAPTURE, _("Capture XForm")),
        (TYPE_UPDATE, _("Update XForm")),
    )
    
    object_id = models.PositiveIntegerField("ID", unique=True)
    id_string = models.CharField(_("ID String/Code"), max_length=30, unique=True)
    title = models.CharField(_("Title"), max_length=50, unique=True)
    type = models.CharField(_("Type"), max_length=1)
    description = models.TextField(_("Description"), null=True)
    is_active = models.BooleanField(default=False)
    api_url = models.URLField(_("API Url"), max_length=100)
    synced_by = models.CharField(max_length=50)
    last_synced = models.DateTimeField(null=True)
    date_imported = models.DateField(null=True)
    
    _non_meta_fields = ['title', 'type', 'description', 'is_active', 
                        'date_imported']
    
    def __str__(self):
        return self.title or self.id_string


class Project(TimeStampedModel):
    """Represents an endeavour to enumerate customers on a high tension (HT)
    PowerLine (Feeder)
    """ 
    
    STATUS_IN_VIEW = 1
    STATUS_IN_PROGRESS = 2
    STATUS_CONCLUDED = 3
    STATUS_REVISITED = 4
    
    STATUS_CHOICES = (
        (STATUS_IN_VIEW, _("In View")),
        (STATUS_IN_PROGRESS, _("In Progress")),
        (STATUS_CONCLUDED, _("Concluded")),
        (STATUS_REVISITED, _("Revisited")),
    )
    
    title = models.CharField(_('Title'), max_length=30, unique=True)
    description = models.TextField(_('Description'), null=True)
    status = models.PositiveSmallIntegerField(_("Status"), 
                choices=STATUS_CHOICES, default=STATUS_IN_VIEW)
    is_active = models.BooleanField(default=True)
    date_started = models.DateField(_('Start Date'))
    date_ended = models.DateField(_('End Date'))
    
    def __str__(self):
        return "{} :: [Project {}]".format(
            self.title, self.get_status_display()
        )


class ProjectXForm(models.Model):
    """Provides relationship between Projects and associated XForms."""
    
    project = models.ForeignKey(Project)
    xform = models.OneToOneField(XForm)
    
    def __str__(self):
        return "{0}: {2} XForm '{1}'".format( 
            self.project.title,
            self.xform.title,
            'Update' if self.xform.type == XForm.TYPE_UPDATE else 'Capture'
        )

