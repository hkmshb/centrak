from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
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
    filter = CaptureFilter(qs_GET, queryset=captures)
    page = paginate(request, filter)

    return render(request, 'enumeration/capture_index.html', {
        'tab': tab, 'captures': page, 'filter': filter
    })


@login_required
def validate_capture(request):    
    acct_no = request.POST.get('acct_no', None)
    if not acct_no or not request.method == 'POST':
        return redirect(reverse('capture-list'))

    acct_no = acct_no.replace('/', '').replace('-', '_')
    if not acct_no.endswith('_01') or len(acct_no) != 13:
        messages.error(request, 'Invalid account number.', extra_tags='danger')
        return redirect(reverse('capture-list'))

    # TODO: validate acct_no format before bringing up form
    return redirect(reverse('capture-upd', args=[acct_no.replace('-','_')]))


@login_required
def manage_capture(request, tab=None, ident=None):
    if not tab and not ident:
        return _manage_capture_new(request)
    if tab == 'new' and ident:
        return _manage_capture_new(request, ident)
    return _manage_capture_exist(request, ident)


def _manage_capture_new(request, id=None):
    capture = None if not id else Capture.objects.get(id=id)
    form = PaperCaptureForm(request.user, Capture.NEW, instance=capture)
    session_key = 'paper_capture_fixed_entries'
    
    if request.method == 'POST':
        try:
            form = PaperCaptureForm(request.user, Capture.NEW, instance=capture, data=request.POST)
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
            form = PaperCaptureForm(request.user, Capture.NEW, instance=capture, initial=fixed_entries)

    return render(request, 'enumeration/capture_form.html', {
        'form': form, 'tab': 'new'
    })


def _manage_capture_exist(request, ident):
    ident = 'f@k3#!' if not ident else ident.replace('_', '-')
    form, instance, acct, initial = (None, None, None, dict())

    # check if account has been validated before
    if ident.endswith('-01'):
        ident = utils.expand_acct_no(ident)
        instance = Capture.objects.filter(acct_no=ident)
        if instance:
            obj_id = str(instance.first().id)
            message = "The Account with number '%s' has been validated before."
            messages.warning(request, message % ident, extra_tags='warning')
            return redirect(reverse('capture-upd', args=[obj_id]))

    if ident.endswith('-01'):
        match = Account.objects.filter(acct_no=ident)
        if not match:
            message = "Account does not exists for '%s'." % ident
            messages.error(request, message, extra_tags='danger')
            return redirect(reverse('capture-list'))
        
        acct = match.first()
        for f in acct._meta.fields:
            initial[f.name] = getattr(acct, f.name)
        
        # normalize entries: acct_no & acct_status
        initial['acct_status'] = Capture.EXISTING
        initial['acct_no'] = utils.expand_acct_no(ident)
        form = PaperCaptureForm(request.user, Capture.EXISTING, initial=initial)
    else:
        instance = Capture.objects.get(id=ident)
        if not instance:
            return redirect(reverse('capture-list'))
        form = PaperCaptureForm(request.user, Capture.EXISTING, instance=instance)
    
    if request.method == 'POST':
        try:
            form = PaperCaptureForm(request.user, Capture.EXISTING, instance=instance, data=request.POST)
            if form.is_valid():
                form.save()

                message = 'Capture updated successfully'
                messages.success(request, message, extra_tags='success')
                return redirect(reverse('capture-list'))
        except Exception as ex:
            messages.error(request, str(ex), extra_tags='danger')

    return render(request, 'enumeration/capture_form.html', {
        'form': form, 'acct': acct, 'tab': 'existing'
    })
    