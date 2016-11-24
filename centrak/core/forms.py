from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django import forms

from .models import UserProfile, Organisation, BusinessOffice, BusinessLevel, \
        ApiServiceInfo
from . import utils


User = get_user_model()

class BaseModelForm(forms.ModelForm):

    def __init__(self, url_cancel=None, *args, **kwargs):
        super(BaseModelForm, self).__init__(*args, **kwargs)
        self.url_cancel = url_cancel

    class Meta:
        abstract = True
    
    @property
    def is_new(self):
        if self.instance:
            return (self.instance.id in ('', None))
        return False

    @property
    def mode(self):
        if self.instance:
            return ("Update" if self.instance.id else "New")
        return ""


class UserProfileForm(BaseModelForm):
    """
    UserProfile creation and change form.
    """

    _error_messages = {
        'invalid-email-domain': _("KEDCO email address required."),
        'invalid-email-format': _(
                "Invalid KEDCO email provided. It does not match expected "
                "format. Contact the CENTrak administrator for help if in "
                "fact the email is an officially assigned email."),
    }

    username = forms.EmailField(label=_('Username/Email'), max_length=50)
    first_name = forms.CharField(label=_('First Name'), max_length=30)
    last_name = forms.CharField(label=_('Last Name'), max_length=30)
    phone = forms.CharField(label=_('Phone'), max_length=50, required=False)
    is_active = forms.BooleanField(label=_('Status: Is Active'), required=False)
    location = forms.ModelChoiceField(label=_("Region"), required=False, 
                    empty_label=mark_safe("&laquo; select &raquo;"),
                    queryset=BusinessOffice.objects.filter(level=BusinessLevel.LEVEL1))
    location1 = forms.ModelChoiceField(label=_("Service Point"), required=False,
                    empty_label=mark_safe("&laquo; select &raquo;"), 
                    queryset=BusinessOffice.objects.filter(level='L2'))
    
    def __init__(self, user, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs['initial'].update({'is_active': user.is_active})
            if instance.location:
                if instance.location.level.code == BusinessLevel.LEVEL2:
                    kwargs['initial'].update({
                        'location':  instance.location.parent.id,
                        'location1': instance.location.id
                    })

        super(UserProfileForm, self).__init__(*args, **kwargs)
        self._current_user = user

        attrs_ = {'class': 'form-control input-sm'}
        for fn, field in self.fields.items():
            if fn != 'is_active':
                field.widget.attrs = attrs_

    class Meta:
        model = UserProfile
        fields = ('username', 'first_name', 'last_name', 'phone', 'is_active', 
                  'location', 'location1')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not self._current_user.is_superuser:
            if not utils.has_valid_email_domain(username):
                msg = self._error_messages['invalid-email-domain']
                raise forms.ValidationError(msg)
        
        try:
            usr = User.objects.get(username=username)
            if self.instance and self.instance.user:
                if usr.id == self.instance.user.id:
                    return username
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("'%s' is already in use.") % username)
    
    def clean(self):
        cleaned_data = super(UserProfileForm, self).clean()
        if not self._current_user.is_superuser:
            fname = cleaned_data.get('first_name')
            lname = cleaned_data.get('last_name')
            email = cleaned_data.get('email')

            if not utils.is_valid_official_email_format(email, fname, lname):
                msg = self._error_messages['invalid-email-format']
                raise forms.ValidationError(msg)
        return cleaned_data

    def save(self, commit=True):
        profile, user = self.instance, self.instance.user
        user.username = self.cleaned_data.get('username')
        user.email = self.cleaned_data.get('username')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.is_active = self.cleaned_data.get('is_active')
        
        location1 = self.cleaned_data.get('location1')
        if hasattr(profile, 'location') and location1:
            profile.location = location1
        
        is_new_user = profile.user.id == None
        try:
            profile.user.save()
            if is_new_user:
                profile.user_id = user.id
            profile.save()
            return profile
        except Exception as ex:
            if is_new_user and profile.user.id:
                profile.user.delete()
            raise ex

class ApiServiceInfoForm(BaseModelForm):
    class Meta:
        model = ApiServiceInfo
        exclude = ['api_token']
        attrs_ = {'class': 'form-control input-sm'}
        attrds = {'class': 'form-control input-sm', 'style': 'height: 139px'}
        widgets = {
            'key': forms.TextInput(attrs=attrs_),
            'title': forms.TextInput(attrs=attrs_),
            'description': forms.Textarea(attrs=attrds),
            'api_root': forms.TextInput(attrs=attrs_),
            'api_auth': forms.TextInput(attrs=attrs_),
            'api_extra': forms.TextInput(attrs=attrs_),
        }

    @property
    def is_new(self):
        if self.instance:
            return (self.instance['key'] in ('', None))
        return False

    @property
    def mode(self):
        if self.instance:
            return ("Update" if self.instance['key'] else "New")
        return ""
    
    def clean_key(self):
        key = self.cleaned_data.get("key")
        if not utils.is_valid_service_key(key):
            message = "The key cannot contain any of these characters: %s"
            raise ValidationError(message % utils.INVALID_SERVICE_KEY_CHAR)
        return key


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
