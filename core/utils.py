from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.contrib import messages



# string const :: view messages
MSG_FMT_SUCCESS_ADD = '%s added successfully.'
MSG_FMT_SUCCESS_UPD = '%s updated successfully.'
MSG_FMT_SUCCESS_DELETE = 'Selected %s deleted successfully.'
MSG_FMT_ERROR_DELETE = 'None of the selected %s were deleted';
MSG_FMT_WARN_DELETE = (
    'Some of the selected %s were delete successfully. '
    'However %s of the selection could not be deleted.')

# string consts :: form messages
REQUIRED_FIELD_ERROR   = 'This field is required.'
REQUIRED_INVALID_ERROR = "Required fields and invalid entries are in red."


# temp constants
class Options:
    PageSize  = 20
    PageSizes = [10, 20, 50, 100, 200]
    

def extend_paginator_page(page, size):
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


def get_paged_object_list(request, model, qsPage='page', qsPageSize='pageSize'):
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
    return extend_paginator_page(objects, page_size)


def manage_object_deletion(request, model, model_name, model_list_url_name, id=None):
    if request.method != 'POST':
        raise Http404('Method type not supported.')
    
    target_ids = list(id or request.POST.getlist('record_ids'))
    if not target_ids:
        return redirect(reverse(model_list_url_name))
    
    failed_ids = []
    for item_id in target_ids:
        try:
            item = model.objects.get(pk=item_id)
            item.delete()
        except ObjectDoesNotExist:
            failed_ids.append(item_id)
    
    target_count = len(target_ids)
    failed_count = len(failed_ids)
    messages.add_message(request,
        level=(messages.SUCCESS if failed_count == 0 else
            messages.WARNING if failed_count < target_count else messages.ERROR),
        message = (MSG_FMT_SUCCESS_DELETE % model_name
            if failed_count == 0 else
                MSG_FMT_WARN_DELETE % (model_name, target_count - failed_count)
                    if failed_count < target_count else
                        MSG_FMT_ERROR_DELETE % model_name),
        extra_tags=('success' if failed_count == 0 else 'warning'
            if failed_count < target_count else 'danger')
    )
    return redirect(reverse(model_list_url_name))

