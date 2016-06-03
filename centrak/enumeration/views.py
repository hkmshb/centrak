import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core import utils
from .models import XForm



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
