from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from core import utils
from .models import XForm



@login_required
def xforms_list(request):
    # TODO: include total captures per XForm
    qset = XForm.objects.filter(is_active=True)
    xforms = utils.paginate(request, qset)
    context = {
        'xforms': xforms
    }
    return render(request, 'enumeration/admin/xforms.html', context)
