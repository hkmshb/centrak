from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from .forms import UserRegistrationForm



#: ===+: account management

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


#: ===+: admin view functions
@login_required
def admin_home(request):
    return render(request, 'main/admin/index.html')


#: ===+: main view functions

def index(request):
    context={}
    return render(request, 'main/index.html', context)
