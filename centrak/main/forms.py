from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

from core import models, utils as core_utils, forms as core_forms

User = get_user_model()



class UserRegistrationForm(UserCreationForm):
    """
    Form for registering/creating a new user for CENTrak.
    """
    
    _error_messages = core_forms.UserProfileForm._error_messages.copy()
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        
        attr_class = 'form-control input-sm'
        for field_name in self._meta.fields:
            field = self.fields[field_name]
            
            field.required = True
            field.widget.attrs['class'] = attr_class
            field.widget.attrs['autocomplete'] = 'off'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not core_utils.has_valid_email_domain(email):
            msg = self._error_messages['invalid-email-domain']
            raise forms.ValidationError(msg)
        
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            _("'%(email)s' is already in use."), 
            params={'email': email})
    
    def clean(self):
        cleaned_data = super(UserRegistrationForm, self).clean()
        fname = cleaned_data.get('first_name')
        lname = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        
        if not core_utils.is_valid_official_email_format(email, fname, lname):
            msg = self._error_messages['invalid-email-format']
            raise forms.ValidationError(msg)
        return cleaned_data
    
    def save(self):
        # TODO: also set default group aka role for user...
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data.get('email')
        user.is_active = False
        user.save()
        
        # create the associated profile
        profile = models.UserProfile(user_id=user.id)
        profile.save()
        return user


class UploadFileForm(forms.Form):
    tag  = forms.CharField(max_length=50, required=False)
    file = forms.FileField(required=True)
