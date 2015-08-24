from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib import messages

from enumeration.models import Manufacturer, MobileOS
from enumeration.forms import ManufacturerForm, MobileOSForm
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from decimal import InvalidOperation


# temp consts
class Options:
    PageSize = 20
    PageSizes = [10, 20, 50, 100, 200] 

    


# string message consts
MSG_SUCCESS_MANUFACTURER_ADD = 'Manufacturer added successfully.'
MSG_SUCCESS_MANUFACTURER_DELETE = 'Selected manufacturer(s) delete successfully.'
MSG_ERROR_MANUFACTURER_DELETE = 'None of the selected manufacturer(s) were deleted';
MSG_WARN_MANUFACTURER_DELETE = (
    'Some of the selected manufacturer(s) were delete successfully. '
    'However %s of the selection could not be deleted.')

MSG_FMT_SUCCESS_ADD = '%s added successfully.'
MSG_FMT_SUCCESS_DELETE = 'Selected %s delete successfully.'
MSG_FMT_ERROR_DELETE = 'None of the selected %s were deleted';
MSG_FMT_WARN_DELETE = (
    'Some of the selected %s were delete successfully. '
    'However %s of the selection could not be deleted.')


def extend_page(page, size):
    page.current_size = str(size)
    page.page_sizes = [str(x) for x in Options.PageSizes]
    
    num_pages = page.paginator.num_pages
    page.paging_numbers = [
        1,
        1 if not page.has_previous() else page.previous_page_number(),
        num_pages if not page.has_next() else page.next_page_number(),
        num_pages
    ]
    return page


def _device_options_tabs():
    return (
        ('Manufacturers', reverse('manufacturers'), 'manufacturers'),
        ('Mobile OS', reverse('mobile-os'), 'mobile-os'),
    )


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
        'enumeration/device-options.html', {
        'record_list': extend_page(manufacturers, page_size),
        'delete_url': reverse('manufacturer-delete'),
        'tabs': _device_options_tabs(),
        'model_name': 'Manufacturer',
        'form': form,
    })


def manufacturer_delete(request, id=None):
    if request.method == 'POST':
        target_ids = list(id or request.POST.getlist('record_ids'))
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


def mobile_os(request):
    if request.method == 'POST':
        form = MobileOSForm(data=request.POST)
        if form.is_valid():
            form.save()
            
            messages.success(request, MSG_FMT_SUCCESS_ADD % 'Mobile OS',
                extra_tags='success')
            
            return redirect(reverse('mobile-os'))
    else:
        form = MobileOSForm()
    
    os_list = MobileOS.objects.all()
    page_size = request.GET.get('pageSize', Options.PageSize)
    paginator = Paginator(os_list, page_size)
    
    page = request.GET.get('page')
    try:
        oses = paginator.page(page)
    except PageNotAnInteger:
        oses = paginator.page(1)
    except EmptyPage:
        oses = paginator.page(paginator.num_pages)
    return render(request,
        'enumeration/device-options.html', {
        'record_list': extend_page(oses, page_size),
        'delete_url': reverse('mobile-os-delete'),
        'tabs': _device_options_tabs(),
        'model_name': 'Mobile OS',
        'form': form
    })
    
    
def mobile_os_delete(request, id=None):
    if request.method != 'POST':
        raise InvalidOperation('Method type not supported')
    
    target_ids = list(id or request.POST.getlist('record_ids'))
    if not target_ids:
        return redirect(reverse('mobile-os'))
    
    failed_ids = []
    for item_id in target_ids:
        try:
            os = MobileOS.objects.get(pk=item_id)
            os.delete()
        except ObjectDoesNotExist:
            failed_ids.append(item_id)
    
    target_count = len(target_ids)
    failed_count = len(failed_ids)
    messages.add_message(request,
        level=(messages.SUCCESS if failed_count == 0 else
            messages.WARNING if failed_count < target_count else messages.ERROR),
        message=(MSG_FMT_SUCCESS_DELETE % 'mobile os'
            if failed_count == 0 else
                MSG_FMT_WARN_DELETE % ('mobile os', target_count - failed_count)
                    if failed_count < target_count else
                        MSG_FMT_ERROR_DELETE % 'mobile os'),
        extra_tags=('success' if failed_count == 0 else 'warning'
            if failed_count < target_count else 'danger')
    )
    return redirect(reverse('mobile-os'))
        