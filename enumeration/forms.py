from django import forms
from enumeration.models import Manufacturer, MobileOS, Device
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
        fiels = ('name',)
        
        widgets = {
            'name': forms.fields.TextInput(attrs={
                        'placeholder': 'Mobile OS Name',
                        'class': 'form-control' })
        }
        error_messages = {
            'name': {'unique': UNIQUE_MOBILEOS_NAME_ERROR}
        }


class DeviceForm(forms.models.ModelForm):
    
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
    
    def clean(self):
        data = super(DeviceForm, self).clean()
        if self.errors:
            self.add_error(None, REQUIRED_INVALID_ERROR)

    def validate_unique(self):
        super(DeviceForm, self).validate_unique()
        if self.errors:
            if '__all__' not in self.errors:
                self.add_error(None, REQUIRED_INVALID_ERROR)
            
            for message in [m for f,m in self.errors.items() if f != '__all__']:
                if str(message).find(REQUIRED_FIELD_ERROR) == -1:
                    self.add_error(None, message)
            
            
