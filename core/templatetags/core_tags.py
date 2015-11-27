from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from core.utils import Options, extend_paginator_page
from ..registry import register



@register.assignment_tag(takes_context=True)
def paginate_records(context, record_list, qsPage='page', qsPageSize='pageSize'):
    request = context['request']
    page_size = request.GET.get(qsPageSize, Options.PageSize)
    page = request.GET.get(qsPage)
    
    paginator = Paginator(record_list, page_size)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    return extend_paginator_page(objects, page_size)

