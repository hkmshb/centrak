from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

from core.models import ApiServiceInfo
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


#: ===+: api services conf
@login_required
def apiservice_survey(request):
    service_key = settings.SURVEY_API_SERVICE_KEY
    try:
        info = ApiServiceInfo.objects.get(pk=service_key)
    except ApiServiceInfo.DoesNotExist:
        info = ApiServiceInfo.objects.create(
                    key=service_key, 
                    api_root=settings.SURVEY_API_ROOT)
    
    # safety-net (?)
    info.api_root = settings.SURVEY_API_ROOT
    
    context = {'info': info }
    return render(request, 'main/admin/api_services.html', context)


@csrf_exempt
def api_services_set_survey_token(request):
    # TODO: provide proper implementation using DRF
    service_key = settings.SURVEY_API_SERVICE_KEY
    if request.method == 'POST':
        data = request.POST.copy()
        print(data.get('value'))
        
        info = ApiServiceInfo.objects.get(pk=service_key)
        info.api_token = data.get('value')
        info.save()
        
        return JsonResponse({
            'message': 'API token applied successfully',
            'api_token': data.get('value')
        })
    return HttpResponseBadRequest()


#: ===+: main view functions

def index(request):
    context={}
    return render(request, 'main/index.html', context)
