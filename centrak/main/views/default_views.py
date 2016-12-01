from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
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
