from django.contrib.auth.decorators import login_required
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from main.forms import UserRegistrationForm



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
    return render(request, 'main/index.html', {})


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
