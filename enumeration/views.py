from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import inlineformset_factory
from django.core.urlresolvers import reverse
from django.forms.utils import ErrorList
from django.http.response import Http404
from django.contrib import messages

from enumeration.models import Manufacturer, MobileOS, Device, DeviceIMEI
from enumeration.forms import ManufacturerForm, MobileOSForm, DeviceForm

from core.utils import get_paged_object_list, manage_object_deletion
from core.utils import MSG_FMT_SUCCESS_ADD, MSG_FMT_SUCCESS_UPD



def _device_options_tabs():
    return (
        ('Manufacturers', reverse('manufacturers'), 'manufacturers'),
        ('Mobile OS', reverse('mobile-os'), 'mobile-os'),
    )


def _update_query_string_fix(request, exclude_list=None, include_qs=None):
    qs = request.GET
    if exclude_list:
        for entry in exclude_list:
            if entry in qs:
                del qs[entry]
    
    if include_qs:
        qs.update(include_qs)
    return qs
    

def devices(request):
    devices = get_paged_object_list(request, Device)
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


def delete_device(request, id=None):
    return manage_object_deletion(request, 
        Device, 'device(s)', 'devices', id)
    

def manufacturers(request):
    if request.method == 'POST':
        form = ManufacturerForm(data=request.POST)
        if form.is_valid():
            form.save()
            
            messages.success(request, MSG_FMT_SUCCESS_ADD % 'Manufacturer',
                extra_tags='success')
            
            return redirect(reverse('manufacturers'))
    else:
        form = ManufacturerForm()
    
    manufacturers = get_paged_object_list(request, Manufacturer)
    return render(request,
        'enumeration/manufacturer-list.html', {
        'record_list': manufacturers,
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
    return manage_object_deletion(request, 
        Manufacturer, 'manufacturer(s)', 'manufacturers', id)


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
    
    os_list = get_paged_object_list(request, MobileOS)
    return render(request,
        'enumeration/mobileos-list.html', {
        'record_list': os_list,
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
    return manage_object_deletion(request, 
        MobileOS, 'mobile os', 'mobile-os', id)

