from django.shortcuts import render

from enumeration.models import Manufacturer, MobileOS



def device_options(request):
    mf_list = Manufacturer.objects.all()
    os_list = MobileOS.objects.all()
    
    return render(request,
        'enumeration/device-options.html', {
            'manufacturer_list': mf_list,
            'mobile_os_list': os_list
        }
    )
