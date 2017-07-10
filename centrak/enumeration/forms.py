import re
from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.db.models import Q
from django import forms

from ezaddress.models import State
from core.models import BusinessOffice, BusinessLevel, Powerline
from .models import XForm, Capture
from .constants import PoleType, PoleCondition, ServiceWireType, \
     ServiceWireCondition, PropertyType, Title, CustomerStatus, \
     Tariff, MeterType, MeterModel, MeterStatus, MeterPhase



# compile regex
## note: (?(1)/|) is a regex if-then-else statement. if `/` is match in 
## capturing group (/)? then `/` is expected else (indicated by |) nothing
## as indicated by nothing before the closing bracket. Thus if `/` is used
## after first 2 digits it expected before the last two digits
## resx: www.regular-expressions.info/conditional.html
_re_book_code = re.compile('^\d{2}(/)?\d{2}(?(1)/|)\d{2}$')



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
    # fields used to indicate if associated entries are fixed
    fx_date_captured   = forms.BooleanField(required=False)
    fx_region_code     = forms.BooleanField(required=False)
    fx_csp_code        = forms.BooleanField(required=False)
    fx_sales_repr_name = forms.BooleanField(required=False)
    fx_csp_supr_name   = forms.BooleanField(required=False)
    fx_tsp_engr_name   = forms.BooleanField(required=False)
    fx_feeder_code     = forms.BooleanField(required=False)
    fx_station_name    = forms.BooleanField(required=False)
    fx_upriser_no      = forms.BooleanField(required=False)
    fx_addr_landmark   = forms.BooleanField(required=False)
    fx_addr_street     = forms.BooleanField(required=False)
    fx_addr_town       = forms.BooleanField(required=False)
    fx_addr_village    = forms.BooleanField(required=False)
    fx_addr_lga        = forms.BooleanField(required=False)
    fx_addr_state_code = forms.BooleanField(required=False)

    id              = forms.CharField(required=False)
    date_captured   = forms.DateField(required=True, label="Date Captured", 
                                      input_formats=['%d/%m/%Y'])
    date_digitized  = forms.DateField(required=True, label="Date Digitized", 
                                      input_formats=['%d/%m/%Y'])
    csp_name        = forms.CharField(required=True, label="CSP")
    sales_repr_name = forms.CharField(required=True, label="Sales Representative")
    csp_supr_name   = forms.CharField(required=True, label="CSP Supervisor")
    tsp_engr_name   = forms.CharField(required=True, label="TSP Engineer")
    region_name     = forms.CharField(required=True, label="Region")
    feeder_name     = forms.CharField(required=True, label="Feeder")
    station_name    = forms.CharField(required=True, label="Station")
    upriser_no      = forms.IntegerField(required=True, label="Upriser #")
    pole_no         = forms.IntegerField(required=True, label="Pole #")

    pole_type       = forms.ChoiceField(required=True, label="Pole Type",
                                        choices=list(PoleType.choices()))
    pole_condition  = forms.ChoiceField(required=False, label="Pole Condition",
                                        choices=list(PoleCondition.choices()))
    swire_type      = forms.ChoiceField(required=True, label="Service Wire Type",
                                        choices=list(ServiceWireType.choices()))
    swire_condition = forms.ChoiceField(required=True, label="Service Wire Condition",
                                        choices=list(ServiceWireCondition.choices()))
    property_type   = forms.ChoiceField(required=True, label="Property Type",
                                        choices=list(PropertyType.choices()))

    title           = forms.ChoiceField(required=True, label="Title",
                                        choices=list(Title.choices()))
    cust_name       = forms.CharField(required=True, label="Customer Name")
    cust_mobile     = forms.CharField(required=False, label="Mobile No")
    cust_email      = forms.EmailField(required=False, label="Customer Email")
    cust_status     = forms.ChoiceField(required=True, label="Status",
                                        choices=list(CustomerStatus.choices()))
    addr_landmark   = forms.CharField(required=False, label="Closest Landmark")
    addr_no         = forms.CharField(required=False, label="House No") 
    addr_street     = forms.CharField(required=True, label="House No")
    addr_town       = forms.CharField(required=False, label="City/Town")
    addr_village    = forms.CharField(required=False, label="Village/Ward")
    addr_lga        = forms.CharField(required=False, label="LGA")
    addr_state      = forms.CharField(required=True, label="State")

    acct_no         = forms.CharField(required=False, label="Account No")
    book_code       = forms.CharField(required=False, label="Book Code")
    acct_status     = forms.CharField(required=True, label="Account Status")
    tariff          = forms.ChoiceField(required=True, label="Tariff",
                                        choices=Tariff.CHOICES)
    amount_to_bill  = forms.FloatField(required=False, label="Amount to bill")
    meter_type      = forms.ChoiceField(required=True, label="Meter Type",
                                        choices=list(MeterType.choices()))
    meter_no        = forms.CharField(required=False, label="Meter No")
    meter_model     = forms.ChoiceField(required=False, label="Meter Model",
                                        choices=list(MeterModel.choices()))
    meter_status    = forms.ChoiceField(required=False, label="Meter Status",
                                        choices=list(MeterStatus.choices()))
    meter_phase     = forms.ChoiceField(required=True, label="Meter Phase",
                                        choices=list(MeterPhase.choices()))

    @staticmethod
    def get_region_choices():
        manager = BusinessOffice.objects
        regions = manager.filter(level=BusinessLevel.LEVEL1).order_by('code')
        return [(r.short_name, r.name) for r in regions]
    
    @staticmethod
    def get_state_choices():
        states = State.objects.all().order_by('id')
        return [(s.code, s.name) for s in states]
    
    @staticmethod
    def get_feeder_choices():
        plines = Powerline.objects.all().order_by('voltage', 'code')
        return [(m.code, "(%s) %s" % (m.get_voltage_display(), m.name)) for m in plines]
    
    @staticmethod
    def get_csp_choices(region):
        criteria = Q(level=BusinessLevel.LEVEL2) \
                 & Q(category=BusinessOffice.CUSTOMER_SERVICE_POINT)
        if region is not None:
            criteria &= Q(parent=region)
        csps = BusinessOffice.objects.filter(criteria).order_by('code')
        return [(o.short_name, o.name) for o in csps]
        
    def __init__(self, user, status, *args, **kwargs):
        # hint: data=POST data
        instance, data, initial = (kwargs.get('instance'), kwargs.get('data'), dict())
        self.instance = instance
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
        
        if 'instance' in kwargs:
            # need to delete instance as the base form is not a ModelForm thus
            # it isn't able to accept instance
            del kwargs['instance']
        super(PaperCaptureForm, self).__init__(*args, **kwargs)
        self.user, self.status = (user, status)
        self._init_fields()

    def _init_fields(self):
        # inner func
        def mk_select_choices(label, choices):
            text = "&laquo; {} &raquo;".format(label)
            return [("", mark_safe(text))] + choices
        
        # add more fields
        user_location = self.user.profile.location
        self.fields['feeder_code'] = forms.ChoiceField(
            required=True, label="Feeder",
            choices=PaperCaptureForm.get_feeder_choices())
        self.fields['csp_code'] = forms.ChoiceField(
            required=True, label="CSP",
            choices=PaperCaptureForm.get_csp_choices(user_location))
        self.fields['region_code'] = forms.ChoiceField(
            required=True, label="Region", 
            choices=PaperCaptureForm.get_region_choices())
        self.fields['addr_state_code'] = forms.ChoiceField(
            required=True, label="State", 
            choices=PaperCaptureForm.get_state_choices())

        # set field attributes
        attrs_ = {'class': 'form-control input-sm'}
        if self.user.profile and self.user.profile.location:
            self.fields['region_code'].initial = user_location.short_name
            self.fields['region_name'].initial = user_location.name

        self.fields['date_digitized'].initial = datetime.today().strftime("%d/%m/%Y")
        self.fields['acct_status'].initial = self.status
        for field_name in ['region_code', 'csp_code', 'feeder_code', 'pole_type',
                           'pole_condition', 'swire_type', 'swire_condition', 
                           'property_type', 'title', 'cust_status', 'addr_state_code', 
                           'tariff', 'meter_type', 'meter_model', 'meter_status',
                           'meter_phase']:
            f = self.fields[field_name]
            f.widget.attrs = attrs_.copy()
            f.widget.attrs['title'] = f.label
            f.widget.choices = mk_select_choices(f.label, f.widget.choices)
        
        if self.status == Capture.NEW:
            self.fields['amount_to_bill'].required = True
        
    def clean_book_code(self):
        value = self.cleaned_data.get('book_code', '').strip()
        if self.status == Capture.NEW:
            if not _re_book_code.match(value):
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

    def clean_amount_to_bill(self):
        value = self.cleaned_data.get('amount_to_bill')
        if self.status == Capture.NEW:
            if int(value) <= 0:
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
    
    def clean(self):
        cleaned_data = super(PaperCaptureForm, self).clean()
        # handle pole condition
        pole_type = cleaned_data.get('pole_type')
        if pole_type == 'none':
            if cleaned_data.get('pole_condition') not in ('', None):
                self.add_error('pole_condition', 'Invalid value')
        elif pole_type is not None:
            if cleaned_data.get('pole_condition') in ('', None):
                self.add_error('pole_condition', 'This field is required.')

        # handle meter type
        meter_type = cleaned_data.get('meter_type')
        if meter_type == 'none':
            for reqf in ('meter_no', 'meter_model', 'meter_status'):
                if cleaned_data.get(reqf) not in ('', None):
                    self.add_error(reqf, 'Invalid value')
        elif meter_type is not None:
            required = ['meter_status']
            if meter_type == 'ppm':
                required.extend(('meter_no', 'meter_model'))
            for reqf in required:
                if cleaned_data.get(reqf) in ('', None):
                    self.add_error(reqf, 'This field is required.')


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
        dropdowns = ('csp', 'feeder')
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

            # handle special case where both field code and name are needed
            f3 = f2.rsplit('_', 1)[0]
            if f3 in dropdowns:
                key = '%s_name' % f3
                entries[key] = data.get(key)

            # extra special for the state
            if f == 'fx_addr_state_code':
                key = 'addr_state'
                entries[key] = data.get(key)

        return entries

    def save(self):
        capture = self._build()
        return capture.save()
