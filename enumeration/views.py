from django.shortcuts import render, redirect

from enumeration.models import Manufacturer
from enumeration.forms import ManufacturerForm
from django.core.urlresolvers import reverse



def manufacturers(request):
    if request.method == 'POST':
        form = ManufacturerForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('manufacturers'))
    else:
        form = ManufacturerForm()
    
    manufacturers = Manufacturer.objects.all()
    return render(request,
        'enumeration/manufacturer-list.html', {
        'manufacturer_list': manufacturers,
        'form': form
    })