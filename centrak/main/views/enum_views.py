from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q as dQ
from mongoengine.queryset import Q

from enumeration.forms import PaperCaptureForm
from enumeration.models import Account, Capture
from core.utils import paginate

from ..filters import CaptureFilter
from .. import utils





@login_required
def capture_index(request, tab=None):
    # clear fixed entry session
    request.session['paper_capture_fixed_entries'] = None

    ## step 1: data filtering
    # filter by current date if no date filter exists
    qs_GET = request.GET.copy()
    date_digitized = qs_GET.get('date_digitized', None)
    if not date_digitized:
        qs_GET['date_digitized'] = datetime.today().strftime('%Y-%m-%d')

    # retrieve paper captures
    status = Capture.EXISTING if not tab else Capture.NEW
    query = Q(medium=Capture.MEDIUM_PAPER) & Q(acct_status=status)

    if not request.user.is_superuser:
        p = request.user.profile
        region_name = p.location.name if p and p.location else ""
        query = query & Q(region_name=region_name) \
              & Q(user_email=request.user.username)

    captures = Capture.objects(query).order_by('-date_digitized')
    filter_ = CaptureFilter(qs_GET, queryset=captures)
    page = paginate(request, filter_)

    ## step 2: stats composition
    stats = {'summary':[], 'history':[]}
    return TemplateResponse(request, 'enumeration/capture_index.html', {
        'tab': tab, 'captures': page, 'filter': filter, 'stats': stats
    })


@login_required
def validate_capture(request):
    lookup = request.POST.get('lookup', '').strip()
    if not lookup or not request.method == 'POST':
        return redirect(reverse('capture-list'))
    
    if not utils.is_acct_no(lookup) and not utils.is_meter_no(lookup):
        err_message = 'Invalid account or meter number.'
        messages.error(request, err_message, extra_tags='danger')
        return redirect(reverse('capture-list'))
    
    # check if record with acct/meter no has been validated before
    predicate = Q(acct_no=utils.expand_acct_no(lookup)) | Q(meter_no=lookup)
    found = Capture.objects.filter(predicate).first()
    if found is not None:
        message = "Record with account or meter number '%s' has been validated before."
        messages.warning(request, message % lookup, extra_tags='warning')
        return redirect(reverse('capture-upd', args=[found.id]))
    
    lookup = lookup.replace('/', '').replace('-', '_')
    return redirect(reverse('capture-upd', args=[lookup]))


@login_required
def manage_capture(request, tab=None, ident=None):
    if not tab and not ident:
        return _manage_capture_new(request)
    if tab == 'new' and ident:
        return _manage_capture_new(request, ident)
    return _manage_capture_exist(request, ident)


def _manage_capture_new(request, capture_id=None):
    capture = None if not capture_id else Capture.objects.get(id=capture_id)
    form = PaperCaptureForm(request.user, Capture.NEW, instance=capture)
    session_key = 'paper_capture_fixed_entries'
    
    if request.method == 'POST':
        try:
            form = PaperCaptureForm(request.user, Capture.NEW, instance=capture, 
                                    data=request.POST)
            if form.is_valid():
                form.save()

                message = 'Capture saved successfully'
                messages.success(request, message, extra_tags='success')
                if 'save_new' in request.POST:
                    # save fixed_entries between requests
                    fixed_entries = form.get_fixed_entries()
                    if fixed_entries:
                        request.session[session_key] = fixed_entries
                    return redirect(reverse('capture-add'))
                else:
                    request.session[session_key] = None
                    return redirect(reverse('capture-list', args=['new/']))
        except Exception as ex:
            messages.error(request, str(ex), extra_tags='danger')
    else:
        fixed_entries = request.session.get(session_key, None)
        if fixed_entries:
            form = PaperCaptureForm(request.user, Capture.NEW, instance=capture, 
                                    initial=fixed_entries)

    return render(request, 'enumeration/capture_form.html', {
        'form': form, 'tab': 'new'
    })


def _manage_capture_exist(request, lookup):
    # hint: lookup can be capture acct_no, meter_no or id
    form, instance, account, initial = (None, None, None, dict())
    args = [request.user, Capture.EXISTING]
    lookup = str(lookup).replace('_', '-')
    if utils.is_acct_no(lookup) or utils.is_meter_no(lookup):
        predicate = dQ(acct_no=utils.expand_acct_no(lookup)) | dQ(meter_no=lookup)
        account = Account.objects.filter(predicate).first()
        if account is None:
            message = "Record with account or meter number '%s' not found."
            messages.error(request, message % lookup, extra_tags='danger')
            return redirect(reverse('capture-list'))
        
        for field in account._meta.fields:
            initial[field.name] = getattr(account, field.name)
        
        # normalize entries: acct_no & acct_status
        initial['acct_status'] = Capture.EXISTING
        if utils.is_acct_no(lookup):
            initial['acct_no'] = utils.expand_acct_no(lookup)
        form = PaperCaptureForm(*args, initial=initial)
    else:
        instance = Capture.objects.get(id=lookup)
        if not instance:
            return redirect(reverse('capture-list'))
        form = PaperCaptureForm(*args, instance=instance)
        
    if request.method == 'POST':
        try:
            form = PaperCaptureForm(*args, instance=instance, data=request.POST)
            if form.is_valid():
                form.save()

                message = 'Capture updated successfully'
                messages.success(request, message, extra_tags='success')
                return redirect(reverse('capture-list'))
        except Exception as ex:
            messages.error(request, str(ex), extra_tags='danger')

    return render(request, 'enumeration/capture_form.html', {
        'form': form, 'acct': account, 'tab': 'existing'
    })
    