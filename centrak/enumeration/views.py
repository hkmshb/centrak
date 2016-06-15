import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core import utils
from .models import XForm, Project
from enumeration.models import Volt, PowerStation



@login_required
def admin_pstations(request):
    tstations = PowerStation.objects(type=PowerStation.TRANSMISSION)
    istations = PowerStation.objects(type=PowerStation.INJECTION)
    
    return render(request, 
        'enumeration/admin/ntwk-pwr-stations.html',{
        'tstations':tstations, 'istations':istations,
        'voltratio': json.dumps(Volt.Ratio.PS_CHOICES),
    })


@login_required
def admin_xforms(request):
    # TODO: include total captures per XForm
    qset = XForm.objects
    context = {
        'xforms': qset
    }
    resp = render(request, 'enumeration/admin/xforms.html', context)
    
    # include survey auth token as cookie
    survey_auth_token = utils.get_survey_auth_token()
    resp.set_cookie('survey_auth_token', survey_auth_token, 60*15)
    return resp


@login_required
def admin_projects(request):
    qset = Project.objects
    xform_qset = XForm.objects(type=XForm.TYPE_CAPTURE, active=True)
    uform_qset = XForm.objects(type=XForm.TYPE_UPDATE, active=True)
    mk_choice = lambda q: [(f.id_string, f.title) for f in q]
    
    context = {
        'projects': qset,
        'choices': json.dumps({
            'status': Project.STATUS_CHOICES,
            'xforms': mk_choice(xform_qset),
            'uforms': mk_choice(uform_qset)
        })
    }
    return render(request, 'enumeration/admin/projects.html', context)

