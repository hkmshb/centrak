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


class Storage(dict):
    """Represents a dictionary object whose elements can be accessed and set 
    using the dot object notation. Thus in addition to `foo['bar']`, `foo.bar` 
    can equally be used.
    """
    
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getattr__(self, key):
        return self.__getitem__(key)
    
    def __setattr__(self, key, value):
        self[key] = value

    def __getitem__(self, key):
        return dict.get(self, key, None)
    
    def __getstate__(self):
        return dict(self)

    def __setstate__(self, value):
        dict.__init__(self, value)

    def __repr__(self):
        return '<Storage %s>' % dict.__repr__(self)
    
    @staticmethod
    def make(obj):
        """Converts all dict-like elements of a dict or storage object into
        storage objects.
        """
        if not isinstance(obj, (dict,)):
            raise ValueError('obj must be a dict or dict-like object')
        
        _make = lambda d: Storage({ k: d[k] 
            if not isinstance(d[k], (dict, Storage))
            else _make(d[k])
                for k in d.keys()
        })
        return _make(obj)

