from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django import forms

from ezaddress.models import State
from core.models import BusinessOffice, BusinessLevel
from .models import XForm, Capture
from .constants import Title, Tariff


class XFormForm(forms.Form):
    """
    Form to validate XForm entries.
    """
    type  = forms.Select(choices=XForm.TYPE_CHOICES)
    title = forms.CharField(label=_('Title'), max_length=100)
    description = forms.Textarea()
    is_active = forms.BooleanField(label=_('Is Active'), initial=False)


class PaperCaptureForm(forms.Form):
    """
    Form to validate entries from paper-based data gathering.
    """
    fx_date_captured   = forms.BooleanField(required=False)
    fx_region_name     = forms.BooleanField(required=False)
    fx_csp_name        = forms.BooleanField(required=False)
    fx_sales_repr_name = forms.BooleanField(required=False)
    fx_csp_supr_name   = forms.BooleanField(required=False)
    fx_tsp_engr_name   = forms.BooleanField(required=False)
    fx_feeder_name     = forms.BooleanField(required=False)
    fx_station_name    = forms.BooleanField(required=False)
    fx_upriser_no      = forms.BooleanField(required=False)
    fx_addr_landmark   = forms.BooleanField(required=False)
    fx_addr_street     = forms.BooleanField(required=False)
    fx_addr_town       = forms.BooleanField(required=False)
    fx_addr_state      = forms.BooleanField(required=False)

    id              = forms.CharField(required=False)
    date_captured   = forms.DateField(required=True, label="Date Captured", input_formats=['%d/%m/%Y'])
    date_digitized  = forms.DateField(required=True, label="Date Digitized", input_formats=['%d/%m/%Y'])
    csp_name        = forms.CharField(required=True, label="CSP")
    sales_repr_name = forms.CharField(required=True, label="Sales Representative")
    csp_supr_name   = forms.CharField(required=True, label="CSP Supervisor")
    tsp_engr_name   = forms.CharField(required=True, label="TSP Engineer")
    feeder_name     = forms.CharField(required=True, label="Feeder")
    station_name    = forms.CharField(required=True, label="Station")
    upriser_no      = forms.IntegerField(required=True, label="Upriser #")
    pole_no         = forms.IntegerField(required=True, label="Pole #")

    acct_no         = forms.CharField(required=False, label="Account No")
    book_code       = forms.CharField(required=False, label="Book Code")
    acct_status     = forms.CharField(required=True, label="Account Status")
    meter_no        = forms.CharField(required=False, label="Meter No")
    title           = forms.ChoiceField(required=True, label="Title", choices=Title.CHOICES)
    cust_name       = forms.CharField(required=True, label="Customer Name")
    cust_mobile     = forms.CharField(required=False, label="Mobile No")
    cust_email      = forms.EmailField(required=False, label="Email")
    addr_landmark   = forms.CharField(required=False, label="Closest Landmark")
    addr_no         = forms.CharField(required=False, label="House No") 
    addr_street     = forms.CharField(required=True, label="House No")
    addr_town       = forms.CharField(required=True, label="City/Town/Village")
    tariff          = forms.ChoiceField(required=True, label="Tariff", choices=Tariff.CHOICES)

    
    @staticmethod
    def get_region_choices():
        regions = BusinessOffice.objects.filter(level=BusinessLevel.LEVEL1).order_by('code')
        return [(r.name, r.name) for r in regions]
    
    @staticmethod
    def get_state_choices():
        states = State.objects.all().order_by('id')
        return [(s.name, s.name) for s in states]

    def __init__(self, user, status, *args, **kwargs):
        instance, data, initial = (kwargs.get('instance'), kwargs.get('data'), dict())
        if instance and not data:
            for f in instance._fields:
                initial[f] = instance[f]
                if f.startswith('date_'):
                    fmt_date = "%d/%m/%Y"
                    if f == 'date_created':
                        initial['date_captured'] = instance[f].strftime(fmt_date)
                    else:
                        initial[f] = instance[f].strftime(fmt_date)

            kwargs['initial'] = initial
            self.instance = instance
        
        if 'instance' in kwargs:
            del kwargs['instance']

        super(PaperCaptureForm, self).__init__(*args, **kwargs)
        self.user, self.status = (user, status)
        self._init_fields()

    
    def _init_fields(self):
        # add more fields
        self.fields['region_name'] = forms.ChoiceField(required=True, label="Region", 
                choices=PaperCaptureForm.get_region_choices())
        self.fields['addr_state'] = forms.ChoiceField(required=True, label="State", 
                choices=PaperCaptureForm.get_state_choices())

        # set field attributes
        choice = [("", mark_safe("&laquo; select &raquo;"))]
        attrs_ = {'class': 'form-control input-sm'}

        if self.user.profile and self.user.profile.location:
            self.fields['region_name'].initial = self.user.profile.location.name

        self.fields['date_digitized'].initial = datetime.today().strftime("%d/%m/%Y")
        self.fields['acct_status'].initial = self.status
        for field_name in ('title', 'tariff', 'region_name', 'addr_state'):
            f = self.fields[field_name]
            f.widget.attrs = attrs_.copy()
            f.widget.attrs['title'] = f.label
            f.widget.choices = choice + f.widget.choices

    def clean_book_code(self):
        value = self.cleaned_data.get('book_code', '').strip()
        if self.status == Capture.NEW:
            if not value or len(value) != 8 or len(value.split('/')) != 3:
                raise forms.ValidationError(_('Invalid value'))
        return value

    def clean_acct_no(self):
        value = self.cleaned_data.get('acct_no', '').strip()
        if self.status == Capture.EXISTING:
            if not value or len(value) != 16:
                raise forms.ValidationError(_('Invalid value'))
            
            if not value.endswith('-01') or len(value.split('/')) != 4:
                raise forms.ValidationError(_('Invalid value'))
        return value

    def clean_sales_repr_name(self):
        return self._clean_human_name('sales_repr_name')
    
    def clean_csp_supr_name(self):
        return self._clean_human_name('csp_supr_name')
    
    def clean_tsp_engr_name(self):
        return self._clean_human_name('tsp_engr_name')
    
    def clean_fullname(self):
        return self._clean_human_name('fullname')

    def _clean_human_name(self, field_name):
        value = self.cleaned_data.get(field_name)
        if not value or len(value) < 3:
            raise forms.ValidationError(_('Invalid value'))
        return value.strip()
    
    def _build(self):
        kwargs, data = (dict(), self.cleaned_data)
        for f in self.fields:
            if f.startswith('fx_'):
                continue
            
            value = data.get(f)
            if not value:
                continue
            
            if f == 'date_captured':
                key = 'date_created'
                kwargs[key] = data.get(f)
                continue
            kwargs[f] = data.get(f)
        
        kwargs['medium'] = Capture.MEDIUM_PAPER
        kwargs['user_email'] = self.user.username
        return Capture(**kwargs)

    def get_fixed_entries(self):
        entries, data = (dict(), self.cleaned_data)
        for f in self.fields:
            if not f.startswith('fx_'):
                continue
            
            value = data.get(f)
            if not value:
                continue
            
            f2 = f.replace('fx_', '')
            value2 = data.get(f2)
            if not value2:
                continue
        
            entries[f] = value
            entries[f2] = value2
            if f == 'fx_date_captured':
                entries[f2] = value2.strftime('%d/%m/%Y')

        return entries

    def save(self):
        capture = self._build()
        return capture.save()
