from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required



@login_required
def capture_index(request, tab=None):
    return render(request, 'enumeration/capture_index.html', {
        'tab': tab
    })

