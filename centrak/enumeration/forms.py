from django.utils.translation import ugettext_lazy as _
from django import forms
from .models import XForm


class XFormForm(forms.Form):
    """
    Form to validate XForm entries.
    """
    type  = forms.Select(choices=XForm.TYPE_CHOICES)
    title = forms.CharField(label=_('Title'), max_length=100)
    description = forms.Textarea()
    is_active = forms.BooleanField(label=_('Is Active'), initial=False)

