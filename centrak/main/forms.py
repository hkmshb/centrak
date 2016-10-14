from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.conf import settings
from django import forms

User = get_user_model()



class UserRegistrationForm(UserCreationForm):
    """Form for registering/creating a new user for CENTrak."""
    
    _error_messages = {
        'invalid-email-domain': _("KEDCO email address required."),
        'invalid-email-format': _(
                "Invalid KEDCO email provided. It does not match expected "
                "format. Contact the CENTrak administrator for help if in "
                "fact the email is an officially assigned email."),
    }
    
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
        if not self.has_valid_email_domain(email):
            msg = self._error_messages['invalid-email-domain']
            raise forms.ValidationError(msg)
        
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(_("'%s' is already in use.") % email)
    
    def clean(self):
        cleaned_data = super(UserRegistrationForm, self).clean()
        fname = cleaned_data.get('first_name')
        lname = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        
        if not self.is_valid_kedco_email_format(email, fname, lname):
            msg = self._error_messages['invalid-email-format']
            raise forms.ValidationError(msg)
        return cleaned_data
    
    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data.get('email')
        user.is_active = False
        # TODO: also set default group aka role for user...
        if commit:
            user.save()
        return user
    
    @staticmethod
    def has_valid_email_domain(email):
        if email:
            domain = email.split('@')[1]
            return domain.lower() in settings.CENTRAK_KEDCO_DOMAINS
        return False
    
    @staticmethod
    def is_valid_kedco_email_format(email, fname, lname):
        if email and fname and lname:
            name_parts = [n for n in (email.split('@')[0]).split('.') if n]
            if len(name_parts) == 2:
                for name in name_parts:
                    if name == fname.lower() or name == lname.lower():
                        return True
        return False


