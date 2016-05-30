from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
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


def get_survey_auth_token():
    key = 'survey'
    content = cache.get(key)
    if content is None:
        from .models import ApiServiceInfo
        try:
            info = ApiServiceInfo.objects.get(pk=key)
            content = info.api_token
        except ApiServiceInfo.DoesNotExist:
            content = None
        
        if content:
            cache.set(key, content, 60 * 15)
    return content

