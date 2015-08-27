from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import inlineformset_factory
from django.core.urlresolvers import reverse
from django.forms.utils import ErrorList
from django.contrib import messages

from enumeration.models import Manufacturer, MobileOS, Device, DeviceIMEI
from enumeration.forms import ManufacturerForm, MobileOSForm, DeviceForm



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
MSG_FMT_SUCCESS_UPD = '%s updated successfully.'
MSG_FMT_SUCCESS_DELETE = 'Selected %s delete successfully.'
MSG_FMT_ERROR_DELETE = 'None of the selected %s were deleted';
MSG_FMT_WARN_DELETE = (
    'Some of the selected %s were delete successfully. '
    'However %s of the selection could not be deleted.')


def _extend_page(page, size):
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


def _get_paged_object_list(request, model, qsPage='page', qsPageSize='pageSize'):
    page_size = request.GET.get(qsPageSize, Options.PageSize)
    page = request.GET.get(qsPage)
    
    object_list = model.objects.all()
    paginator = Paginator(object_list, page_size)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    return _extend_page(objects, page_size)
    

def devices(request):
    devices = _get_paged_object_list(request, Device)
    return render(request,
        'enumeration/device-list.html', {
        'record_list': devices
    })

def manage_device(request, id=None):
    device = (Device() if not id else Device.objects.get(pk=id))
    IMEIInlineFormSet = inlineformset_factory(Device, DeviceIMEI, extra=2, max_num=2)
        
    if request.method == 'POST':
        device_form = DeviceForm(data=request.POST, instance=device)
        formset = IMEIInlineFormSet(request.POST, request.FILES, instance=device)        
                
        if device_form.is_valid():
            target_device = device_form.save(commit=False)
            formset = IMEIInlineFormSet(request.POST, request.FILES, instance=target_device)
            
            if formset.is_valid():
                target_device.save()
                formset.save()
                
                msg_fmt = MSG_FMT_SUCCESS_ADD if not id else MSG_FMT_SUCCESS_UPD
                messages.success(request, msg_fmt % 'Device', extra_tags='success')
            
                urlname = ('devices' if 'btn_save' in request.POST else 'device-insert')
                return redirect(reverse(urlname))
    else:
        device_form = DeviceForm(instance=device)
        formset = IMEIInlineFormSet(instance=device)
        
    # transfer formset errors to device_form errors because only these are
    # rendered in the template.
    formset_errors = [d for d in formset.errors if d]
    if formset_errors:
        current = device_form.errors.get('__all__', ErrorList())
        current.append('A device with the IMEI already exists.');
        device_form.errors['__all__'] = current
    
    return render(request, 'enumeration/device-form.html', {
        'form': device_form, 'imei_formset': formset,
    })


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
        'record_list': _extend_page(manufacturers, page_size),
        'tabs': _device_options_tabs(),
        'form': form,
    })


def manufacturer_update(request, id):
    manufacturer = get_object_or_404(Manufacturer, pk=id)
    model_name = 'Manufacturer'
    
    if request.method == 'POST':
        form = ManufacturerForm(request.POST, instance=manufacturer)
        if form.is_valid():
            form.save()
            
            messages.success(request, MSG_FMT_SUCCESS_UPD % model_name,
                extra_tags='success')
    else:
        form = ManufacturerForm(instance=manufacturer)
    return render(request,
        'enumeration/manufacturer-form.html', {
        'model_name': model_name,
        'form': form
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
        'enumeration/mobileos-list.html', {
        'record_list': _extend_page(oses, page_size),
        'tabs': _device_options_tabs(),
        'form': form
    })


def mobile_os_update(request, id):
    os = get_object_or_404(MobileOS, pk=id)
    model_name = 'Mobile OS'
    
    if request.method == 'POST':
        form = MobileOSForm(request.POST, instance=os)
        if form.is_valid():
            form.save()
            
            messages.success(request, MSG_FMT_SUCCESS_UPD % model_name,
                extra_tags='success')
            
            return redirect(reverse('mobile-os'))
    else:
        form = MobileOSForm(instance=os)
    return render(request,
        'enumeration/mobileos-form.html', {
        'model_name': model_name,
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
        