from django import forms
from enumeration.models import Manufacturer, MobileOS, Device, Person, Team, \
        MemberRole
from django.core.exceptions import ValidationError



# const error messages
UNIQUE_MANUFACTURER_NAME_ERROR = 'Manufacturer name already exist.'
UNIQUE_MOBILEOS_NAME_ERROR     = 'Mobile OS name already exists.'

REQUIRED_FIELD_ERROR   = 'This field is required.'
REQUIRED_INVALID_ERROR = "Required fields and invalid entries are in red."
UNIQUE_SERIALNO_ERROR  = "Serial # already exist."
UNIQUE_LABEL_ERROR     = "Label already exist."



class ManufacturerForm(forms.models.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ('name',)
        
        widgets = {
            'name': forms.fields.TextInput(attrs={
                        'placeholder': 'Manufacturer Name',
                        'class': 'form-control' })
        }
        error_messages = {
            'name': {'unique': UNIQUE_MANUFACTURER_NAME_ERROR }
        }
    

class MobileOSForm(forms.models.ModelForm):
    class Meta:
        model = MobileOS
        fields = ('name',)
        
        widgets = {
            'name': forms.fields.TextInput(attrs={
                        'placeholder': 'Mobile OS Name',
                        'class': 'form-control' })
        }
        error_messages = {
            'name': {'unique': UNIQUE_MOBILEOS_NAME_ERROR}
        }


class ModelForm(forms.models.ModelForm):
    
    def clean(self):
        super(ModelForm, self).clean()
        if self.errors:
            self.add_error(None, REQUIRED_INVALID_ERROR)

    def validate_unique(self):
        super(ModelForm, self).validate_unique()
        if self.errors:
            if '__all__' not in self.errors:
                self.add_error(None, REQUIRED_INVALID_ERROR)
            
            for message in [m for f,m in self.errors.items() if f != '__all__']:
                if str(message).find(REQUIRED_FIELD_ERROR) == -1:
                    self.add_error(None, message)


class DeviceForm(ModelForm):
    
    class Meta:
        model = Device
        fields = ('form_factor', 'serialno', 'label', 'brand', 'model', 
                  'mobile_os', 'os_version', 'notes')
        
        _attrs = {'class': 'form-control input-sm'}
        widgets = {
            'form_factor': forms.fields.Select(attrs=_attrs),
            'serialno': forms.fields.TextInput(attrs=_attrs),
            'label': forms.fields.TextInput(attrs=_attrs),
            'brand': forms.fields.Select(attrs=_attrs),
            'model': forms.fields.TextInput(attrs=_attrs),
            'mobile_os': forms.fields.Select(attrs=_attrs),
            'os_version': forms.fields.TextInput(attrs=_attrs),
            'notes': forms.Textarea(attrs={ 
                        'class': 'form-control input-sm', 'rows': '3'}),
        }
        error_messages = {
            'serialno': {'unique': UNIQUE_SERIALNO_ERROR },
            'label':    {'unique': UNIQUE_LABEL_ERROR },
        }
            
            
class PersonForm(ModelForm):
    
    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'gender', 'official_status',
                  'location', 'mobile', 'mobile2', 'email')
        _attrs = {'class': 'form-control input-sm'}
        widgets = {
            'first_name': forms.fields.TextInput(attrs=_attrs),
            'last_name':  forms.fields.TextInput(attrs=_attrs),
            'gender':     forms.fields.Select(attrs=_attrs),
            'official_status': forms.fields.Select(attrs=_attrs),
            'location':   forms.fields.Select(attrs=_attrs),
            'mobile':     forms.fields.TextInput(attrs=_attrs),
            'mobile2':    forms.fields.TextInput(attrs=_attrs),
            'email':      forms.fields.EmailInput(attrs=_attrs),
        }

class TeamForm(ModelForm):
    
    class Meta:
        model = Team
        fields = ('code', 'name')
        _attrs = {'class': 'form-control input-sm'}
        widgets = {
            'code': forms.fields.TextInput(attrs=_attrs),
            'name': forms.fields.TextInput(attrs=_attrs)
        }

        
class MemberRoleForm(ModelForm):
    
    class Meta:
        model = MemberRole
        fields = ('name', 'description')
        _attrs = {'class': 'form-control input-sm'}
        widgets = {
            'name': forms.fields.TextInput(attrs=_attrs),
            'description': forms.Textarea(attrs={
                    'class': 'form-control input-sm', 'rows': '3'}),
        }

