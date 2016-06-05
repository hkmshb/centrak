import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core import utils
from .models import XForm
from enumeration.models import PowerStation



@login_required
def network_ps(request):
    tstations = PowerStation.objects(type=PowerStation.TRANSMISSION)
    istations = PowerStation.objects(type=PowerStation.INJECTION)
    context = {'tstations': tstations, 'istations': istations }
    return render(request, 
        'enumeration/admin/ntwk-pwr-stations.html',
        context
    )


@login_required
def xforms_list(request):
    # TODO: include total captures per XForm
    qset = XForm.objects
    context = {
        'xforms': qset
    }
    response = render(request, 'enumeration/admin/xforms.html', context)
    
    # include survey auth token as cookie
    survey_auth_token = utils.get_survey_auth_token()
    response.set_cookie('survey_auth_token', survey_auth_token, 60*15)
    return response
