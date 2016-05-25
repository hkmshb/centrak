from django.shortcuts import render



def xforms_list(request):
    return render(request, 'enumeration/admin/xforms.html')
