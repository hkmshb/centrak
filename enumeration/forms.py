from django import forms
from enumeration.models import Manufacturer



# const error messages
UNIQUE_MANUFACTURER_NAME_ERROR = 'Manufacturer name already exist.'



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
    
    