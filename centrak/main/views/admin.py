from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

from ezaddress.models import State
from core.models import ApiServiceInfo, BusinessLevel, BusinessOffice, Organization



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


def get_org_or_create_default():
    org = Organization.objects.first()
    if not org:
        org = Organization.objects.create(
                name='<CENTrak>', email='<info@domain>',
                phone='<080-0000-0000>', website='<http://domain>', 
                addr_street='<Address Street>', addr_town='<Address Town>',
                postal_code='<700000>', addr_state=None)
    return org

@login_required
def admin_org(request):
    org = get_org_or_create_default
    states = State.objects.all() 
    return render(request, 'main/admin/org_info.html', {
        'org': org,
        'states': [{'id': x.id, 'name': x.name, 'country': x.country.name} 
                    for x in states]
    })


@login_required
def admin_offices(request):
    offices = BusinessOffice.objects.filter(level=BusinessLevel.LEVEL1)\
                            .order_by('code')
    states = State.objects.all()
    return render(request, 'main/admin/org_offices.html', {
        'offices': offices,
        'states': [{'id': x.id, 'name': x.name, 'country': x.country.name}
                    for x in states]
    })
