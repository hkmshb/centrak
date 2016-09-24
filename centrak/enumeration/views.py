import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.cache import cache

from mongoengine.queryset import Q

from core import utils
from .models import XForm, Project
from enumeration.models import Volt, PowerStation, Capture, Update



#: ==+: admin view funcs :+==
@login_required
def admin_pstations(request):
    tstations = PowerStation.objects(type=PowerStation.TRANSMISSION)
    istations = PowerStation.objects(type=PowerStation.INJECTION)
    
    return render(request, 
        'enumeration/admin/ntwk-powerstations.html',{
        'tstations':tstations, 'istations':istations,
        'voltratio': json.dumps(Volt.Ratio.PS_CHOICES),
    })


@login_required
def admin_xforms(request):
    # TODO: include total captures per XForm
    xforms = XForm.objects
    
    # build stats dict
    stats_ = {}
    for f in xforms:
        key = 'project.{}.form.{}'.format(f.id_string[:4], f.id_string)
        model, main_qs = Capture, Q(_xform_id_string=f.id_string)
        if '_cf' not in f.id_string:
            model = Update
            main_qs = main_qs & (Q(dropped__ne=True) & Q(merged__ne=True))
            
        stat = cache.get(key)
        if stat is None:
            count = model.objects(main_qs).count()
            stat = {'count': count}
        stats_[f.id_string] = {'count': stat['count']}
    
    context = {
        'xforms': xforms,
        'stats': json.dumps(stats_)
    }
    resp = render(request, 'enumeration/admin/xforms.html', context)
    
    # include survey auth token as cookie
    survey_auth_token = utils.get_survey_auth_token()
    resp.set_cookie('survey_auth_token', survey_auth_token, 60*15)
    return resp


@login_required
def admin_projects(request):
    projects = Project.objects
    xform_qset = XForm.objects(type=XForm.TYPE_CAPTURE, active=True)
    uform_qset = XForm.objects(type=XForm.TYPE_UPDATE, active=True)
    mk_choice = lambda q: [(f.id_string, f.title) for f in q]
    
    # build stats dict
    stats_ = {}
    for p in projects:
        key = 'project.{}'.format(p.code)
        stat = cache.get(key)
        if stat is None:
            count = Capture.objects(project_id__startswith=p.code).count()
            stat = {'count': count}
        stats_[p.code] = {'count': stat['count']}
    
    context = {
        'projects': projects,
        'stats': json.dumps(stats_),
        'choices': json.dumps({
            'status': Project.STATUS_CHOICES,
            'xforms': mk_choice(xform_qset),
            'uforms': mk_choice(uform_qset)
        })
    }
    return render(request, 'enumeration/admin/projects.html', context)

