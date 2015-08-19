from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib import messages

from enumeration.models import Manufacturer
from enumeration.forms import ManufacturerForm
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from decimal import InvalidOperation


# temp consts
class Options:
    PageSize = 20
    
    


# string message consts
MSG_SUCCESS_MANUFACTURER_ADD = 'Manufacturer added successfully.'
MSG_SUCCESS_MANUFACTURER_DELETE = 'Selected manufacturer(s) delete successfully.'
MSG_ERROR_MANUFACTURER_DELETE = 'None of the selected manufacturer(s) were deleted';
MSG_WARN_MANUFACTURER_DELETE = (
    'Some of the selected manufacturer(s) were delete successfully. '
    'However %s of the selection could not be deleted.')


def manufacturers(request):
    if request.method == 'POST':
        form = ManufacturerForm(data=request.POST)
        if form.is_valid():
            form.save()
            
            messages.success(request, MSG_SUCCESS_MANUFACTURER_ADD,
                extra_tags='success')
            
            return redirect(reverse('manufacturers'))
    else:
        form = ManufacturerForm()
    
    manufacturer_list = Manufacturer.objects.all()
    page_size = request.GET.get('pageSize', Options.PageSize)
    paginator = Paginator(manufacturer_list, page_size)
    
    page = request.GET.get('page')
    try:
        manufacturers = paginator.page(page)
    except PageNotAnInteger:
        manufacturers = paginator.page(1)
    except EmptyPage:
        manufacturers = paginator.page(paginator.num_pages)
    return render(request,
        'enumeration/manufacturer-list.html', {
        'manufacturer_list': manufacturers,
        'form': form
    })


def manufacturer_delete(request, id=None):
    if request.method == 'POST':
        target_ids = list(id or request.POST.getlist('manufacturer_ids'))
        if not target_ids:
            return redirect(reverse('manufacturers'))
        
        failed_ids = []
        for item_id in target_ids:
            try:
                manufacturer = Manufacturer.objects.get(pk=item_id)
                manufacturer.delete()
            except ObjectDoesNotExist:
                failed_ids.append(item_id)
        
        target_count = len(target_ids)
        failed_count = len(failed_ids)
        messages.add_message(request,
            level=(messages.SUCCESS if failed_count == 0 else
                messages.WARNING if failed_count < target_count else messages.ERROR),
            message= (MSG_SUCCESS_MANUFACTURER_DELETE
                if failed_count == 0 else 
                    MSG_WARN_MANUFACTURER_DELETE % (target_count - failed_count)
                        if failed_count < target_count else
                            MSG_ERROR_MANUFACTURER_DELETE),
            extra_tags=('success' if failed_count == 0 else 'warning'
                if failed_count < target_count else 'danger')
        )
        return redirect(reverse('manufacturers'))
    raise InvalidOperation('Method type not supported')



    