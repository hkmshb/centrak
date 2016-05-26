from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings



def paginate(request, query_set, page_size=None):
    if not page_size:
        page_size = settings.CENTRAK_TABLE_PAGE_SIZE
    
    paginator = Paginator(query_set, page_size)
    page = request.GET.get('page')
    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        # page value not an integer
        records = paginator.page(1)
    except EmptyPage:
        # requested page exceeds pages available
        records = paginator.page(paginator.num_pages)
    return records
