from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from core.utils import admin_with_permission, has_object_permission
from core.models import ApiServiceInfo
from .models import XForm



@admin_with_permission()
def xform_list(request, tab=None):
    context, template = ({'tab': tab}, 'enumeration/admin/xform_list.html')
    if not tab or tab == 'imported':
        context['xforms'] = XForm.objects.order_by('object_id')
        return render(request, template, context)

    #: bootstrap env for js processing
    service = get_object_or_404(ApiServiceInfo, pk='survey')
    context['survey_api_root'] = service.api_root
    context['xforms_endpoint'] = reverse('xform-list')
    context['object_ids'] = [x.object_id for x in XForm.objects.only('object_id')]
    resp = render(request, 'enumeration/admin/xform_list.html', context)
    
    # include survey auth toke as cookies
    resp.set_cookie('survey_auth_token', service.api_token)
    return resp


@admin_with_permission()
def xform_detail(request, xform_id):
    xform = get_object_or_404(XForm, pk=xform_id)
    return render(request, 'enumeration/admin/xform_detail.html', {
        'xform': xform
    })

@admin_with_permission()
def manage_xform(request, xform_id=None):
    pass


