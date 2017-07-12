from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from dolfin.core import Storage

from main.forms import UserRegistrationForm
from enumeration.models import Capture
from core.models import Notification
from core.utils import paginate
from stats import core as stcore


#: ==+: account management
def register_account(request):
    form = UserRegistrationForm()
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('registration-complete'))
        
    context = {'form': form}
    return render(request, 'account/registration_form.html', context)


def registration_complete(request):
    return render(request, 'account/registration_complete.html')


def password_reset(request):
    return render(request, 'account/password_reset.html')


#: ==+: custom error pages
def handle_bad_request(request):
    """Services bad requests"""
    return render(request, '400.html')


def handle_access_denied(request):
    """Services bad requests"""
    return render(request, '403.html')


def handle_not_found(request):
    """Services page not found requests"""
    return render(request, '404.html')


def handle_server_error(request):
    """Services server error requests"""
    return render(request, '500.html')


#: ==+: main view functions
def index(request):
    ### non authenticated user
    user = request.user
    if user is None or not user.is_authenticated or user.is_anonymous():
        return TemplateResponse(request, 'main/index.html', {})

    ### authenticated user
    ## collect location
    loc = user.profile.location

    ## stats: computation for stats on dashboard
    fields = ['region_code', 'acct_status', 'date_created']
    captures_qs = Capture.objects.only(*fields)
    df = stcore.queryset_to_dataframe(captures_qs)
    summary = stcore.stats_dash_capture_summary(df, loc and loc.short_name)
    analytics = stcore.stats_dash_capture_analytics(df)

    # inline func
    mp = lambda p,t: ((p or 0)/(t or 1)) * 100

    # TODO: retrive target from settings
    target = 10000

    ## stats processing: summary
    # company wide
    summary_entries = []
    for key in ['total', 'existing', 'new']:
        entry = (key, target, summary[key], mp(summary[key], target))
        summary_entries.append(entry)
    
    # region
    key, total = 'total:region', summary['total:region']
    summary_entries.append((key, target, total, mp(total, target)))

    ## stats processing: analytics
    # company wide
    analytics_entries = {}
    for key, stats_data in analytics.items():
        labels = [lbl for lbl in sorted(analytics[key].keys()) if lbl != '_total_']
        figures = [['_total_', []], ['existing', []], ['new', []]]
        for label in labels:
            for k, store in figures:
                store.append(stats_data[label].get(k, 0))
        analytics_entries[key] = [labels, figures]
        
    return TemplateResponse(request, 'main/index.html', {
        'stats': {'summary': summary_entries, 'analytics': analytics_entries}
    })


@login_required
def profile_manage_passwd(request):
    def _style_form(form):
        attrs_ = {'class': 'form-control input-sm'}
        for fn in ['old_password', 'new_password1', 'new_password2']:
            field = form.fields.get(fn)
            if field:
                label = 'Confirm password' if '2' in fn else field.label
                attrs_['placeholder'] = label
                field.widget.attrs = attrs_.copy()
    
    form = auth_forms.PasswordChangeForm(request.user)
    if request.method == 'POST':
        form = auth_forms.PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()

            message = "Password has been changed successfully"
            messages.success(request, message, extra_tags='success')
            return auth_views.logout(request, next_page='profile-upd')
        else:
            messages.error(request, form.errors.as_text(), extra_tags='danger')
    
    _style_form(form)
    return render(request, 'main/profile_detail.html', {
        'user': request.user, 'form_pwd': form
    })


@login_required
def notification_list(request):
    q = Notification.objects.filter(user_id=request.user.id).order_by('-id')
    p = paginate(request, q)
    return render(request, 'main/notification_list.html', {
        'notifications': p
    })
    

@login_required
def notification_detail(request, id):
    notification = Notification.objects.get(user_id=request.user.id, id=id)
    notification.read = True
    notification.save()
    return render(request, 'main/notification_detail.html', {
        'notification': notification
    })
