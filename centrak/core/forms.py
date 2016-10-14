from django import forms
from .models import Organisation, BusinessOffice



class BaseModelForm(forms.ModelForm):

    def __init__(self, url_cancel=None, *args, **kwargs):
        super(BaseModelForm, self).__init__(*args, **kwargs)
        self.url_cancel = url_cancel

    class Meta:
        abstract = True
    
    @property
    def is_new(self):
        if self.instance:
            return (self.instance.id not in (None, ''))
        return False

    @property
    def mode(self):
        if self.instance:
            return ("Update" if self.instance.id else "New")
        return ""


class BusinessEntityForm(BaseModelForm):
    """Form for updating organisation model object."""

    class Meta:
        abstract = True
        fields = ('name', 'phone', 'email', 'website', 'addr_street',
                  'addr_town', 'postal_code', 'addr_state')
        attrs_ = {'class': 'form-control input-sm'}
        widgets = {
            'name': forms.TextInput(attrs=attrs_),
            'phone': forms.TextInput(attrs=attrs_),
            'email': forms.EmailInput(attrs=attrs_),
            'website': forms.URLInput(attrs=attrs_),
            'addr_street': forms.TextInput(attrs=attrs_),
            'addr_town': forms.TextInput(attrs=attrs_),
            'postal_code': forms.TextInput(attrs=attrs_),
            'addr_state': forms.Select(attrs=attrs_)
        }


class OrganisationForm(BusinessEntityForm):
    """Form for managing organisation model object."""

    def __init__(self, *args, **kwargs):
        super(BusinessEntityForm, self).__init__(*args, **kwargs)
        self.fields['short_name'].widget.attrs = {'class': 'form-control input-sm'}

    class Meta(BusinessEntityForm.Meta):
        model = Organisation
        fields = ('short_name',) + BusinessEntityForm.Meta.fields


class OfficeForm(BusinessEntityForm):
    """Form for managing office model objects."""

    def __init__(self, *args, **kwargs):
        super(BusinessEntityForm, self).__init__(*args, **kwargs)
        attrs = BusinessEntityForm.Meta.attrs_
        self.fields['code'].widget.attrs = attrs
        self.fields['level'].widget.attrs = attrs
        self.fields['parent'].widget.attrs = attrs
        self.fields['category'].widget.attrs = attrs

    class Meta(BusinessEntityForm.Meta):
        model = BusinessOffice
        fields = ('code', 'level', 'parent', 'category') \
               + BusinessEntityForm.Meta.fields
