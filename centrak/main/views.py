from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

from enumeration.models import Project, XForm
from enumeration.services import import_surveys

from core.models import ApiServiceInfo
from core.utils import MessageList
from .forms import UserRegistrationForm
from . import stats, services



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


@login_required
def projects_list(request):
    projects = (Project.objects(active=True)
                       .only('code','name','xforms','uforms'))
    
    stats_ = {}
    for p in projects:
        key = 'project.{}'.format(p.code)
        stat = cache.get(key)
        if stat is None:
            stat = stats.for_project(p, key)
            cache.set(key, stat, 60 * 30)
        stats_[p.code] = stat
        
    context = {
        'projects': projects,
        'stats': stats_
    }
    return render(request, 'main/projects/listing.html', context)


@login_required
def projects_xform_list(request, code):
    project, xforms, stats_ = (Project.objects.get(code=code), [], {})
    xform_ids = (project.xforms or [])[:] + (project.uforms or [])[:]
    
    if request.method == 'POST':
        xforms_to_sync = request.POST.getlist('xform_id', [])
        if not xforms_to_sync:
            message = 'Need to select at least 1 form to sycn.'
            messages.error(request, message, extra_tags='danger')
        else:
            username = request.user.username
            results = import_surveys(xforms_to_sync, username)
            cache.delete("project.{}".format(project.code))
            
            xforms_info = list(XForm.objects(id_string__in=xforms_to_sync)
                                    .order_by('type', 'title')
                                    .only('id_string', 'title')) 
            
            smessages, fmessages = MessageList(), MessageList()
            for xf_info in xforms_info:
                cache.delete("project.{}.form.{}".format(project.code, xf_info.id_string))
                result = results.get(xf_info.id_string)
                if not result.errors:
                    msg = "{} surveys imported for {}".format(result.count, xf_info.title)
                    smessages.append(msg)
                else:
                    msg = "{} Error: {}".format(xf_info.title, result.errors)
                    fmessages.append(msg)
            
            if smessages:
                messages.success(request, smessages, extra_tags='success')
            else:
                messages.error(request, fmessages, extra_tags='danger')
        return redirect(reverse('projects-xform-list', kwargs={'code':code}))
    
    for xform_id in xform_ids:
        key = "project.{}.form.{}".format(project.code, xform_id)
        xform = XForm.objects.get(id_string=xform_id)
        xforms.append(xform)
        
        stat = cache.get(key)
        if stat is None:
            stat = stats.for_project_xform(xform, key)
            cache.set(key, stat, 60 * 30)
        stats_[xform_id] = stat
    
    context = {
        'project': project,
        'xforms': xforms,
        'stats': stats_
    }
    return render(request, 'main/projects/xforms-listing.html', context)

