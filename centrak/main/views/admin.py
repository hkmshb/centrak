from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


#: ==+: admin view functions
@login_required
def admin_home(request):
    return render(request, 'main/admin/index.html')

