from django import forms
from core.models import Organization
from core.utils import REQUIRED_FIELD_ERROR, REQUIRED_INVALID_ERROR



class OrganizationForm(forms.models.ModelForm):
    class Meta:
        model = Organization
        fields = ('name', 'email', 'phone', 'url', 'street1', 'street2', 
                  'city', 'state', 'note')
        attrs_ = {'class': 'form-control input-sm'}
        widgets = {
            'name': forms.fields.TextInput(attrs=attrs_),
            'email': forms.fields.EmailInput(attrs=attrs_),
            'url': forms.fields.URLInput(attrs=attrs_),
            'phone': forms.fields.TextInput(attrs=attrs_),
            'street1': forms.fields.TextInput(attrs=attrs_),
            'street2': forms.fields.TextInput(attrs=attrs_),
            'city': forms.fields.TextInput(attrs=attrs_),
            'state': forms.fields.Select(attrs=attrs_),
            'note': forms.Textarea(attrs={
                        'class': 'form-control input-sm', 'rows': '3' }),
        }
    
    def clean(self):
        data = super(OrganizationForm, self).clean()
        if self.errors:
            self.add_error(None, REQUIRED_INVALID_ERROR)
    
    def validate_unique(self):
        super(OrganizationForm, self).validate_unique()
        if self.errors:
            if '__all__' not in self.errors:
                self.add_error(None, REQUIRED_INVALID_ERROR)
            
            for message in [m for f,m in self.errors.items() if f != '__all__']:
                if str(message).find(REQUIRED_FIELD_ERROR) == -1:
                    self.add_error(None, message)

    