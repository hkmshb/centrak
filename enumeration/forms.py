from django import forms
from enumeration.models import Manufacturer, MobileOS



# const error messages
UNIQUE_MANUFACTURER_NAME_ERROR = 'Manufacturer name already exist.'
UNIQUE_MOBILEOS_NAME_ERROR     = 'Mobile OS name already exists.'



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

