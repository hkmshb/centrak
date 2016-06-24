import json
import logging
import requests
from urllib.parse import urlencode, urljoin

try:
    from collections import UserList
except ImportError:
    from UserList import UserList

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import SafeString
from django.core.cache import cache
from django.conf import settings
from django import template


# global tag filter register
tag_registerer = template.Library()



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


class MessageList(UserList, list):
    """
    A collection of messages that know how to display itself in various formats.
    """
    def __init__(self, initlist=None, msg_class=None):
        super(MessageList, self).__init__(initlist)
        self.msg_class = 'msglist'
        if msg_class:
            self.msg_class += " {}".format(msg_class)
    
    def as_ul(self):
        if not self.data:
            return ''
        
        return SafeString('<ul class="{}">{}</ul>'.format(
            self.msg_class,
            ''.join('<li>{}</li>'.format(str(m)) for m in self)
        ))
    
    def __str__(self):
        if not self.data or isinstance(self.data, str):
            return ''
        return self.as_ul()


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


class ApiClient(object):

    def __init__(self, api_urlbase, token):
        assert token not in (None, "")
        self.api_urlbase = api_urlbase
        self.token = token

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': 'Token ' + self.token
        })
    
    def count(self, url_subpath, query):
        return self.get(url_subpath, query, get_count=True)
    
    def get_survey(self, xform_id, date_captured=None, get_count=False, start=0):
        try:
            urlsubpath = "{}".format(xform_id)
            query = {}
            if date_captured:
                query = {'datetime_today': date_captured}
            return self.get(urlsubpath, query, get_count, start)
        except Exception as ex:
            logging.error("Error (ApiClient.get_survey): %s" % str(ex))
            return []

    def get(self, url_subpath, query, get_count=False, start=0, limit=100):
        urlpath = urljoin(self.api_urlbase + '/', url_subpath)

        def _get_records(start_at):
            params = {'start': start_at, 'limit': limit}
            if query:
                params.update({'query': json.dumps(query) })
            
            url_full = "{}?{}".format(urlpath, urlencode(params))
            resp = self.session.get(url_full)
            return resp.json()
        
        def _get_scalar():
            params = {'count': 1}
            if query:
                params.update({'query': json.dumps(query)})
            
            url_full = "{}?{}".format(urlpath, urlencode(params))
            resp = self.session.get(url_full)
            return len(resp.json())
        
        if get_count:
            return _get_scalar()
        
        data = _get_records(start)
        yield data

        while (len(data) == limit):
            start += limit
            data = _get_records(start)
            yield data
