from collections import namedtuple

from django.utils.translation import ugettext_lazy as _
from django.utils.functional import SimpleLazyObject
from django.core.urlresolvers import reverse
from django.conf import settings



class Menu(object):
    """Defines the application menu."""
    
    class Item(namedtuple('Item', ['menu', 'text', 'url', 'children'])):
        
        def __new__(cls, menu, text, url=None, children=None):
            kwargs = {'menu': menu, 'text': text,  'url': url or '', 
                      'children': children or []}
            item = super(Menu.Item, cls).__new__(cls, **kwargs)
            return item
        
        def is_active(self):
            default_if_none_url = '_/_'
            item_url = self.url or default_if_none_url
            
            request_root_url = self.menu._request_path.split('/')[1]
            item_root_url = item_url.split('/')[1]
            return item_root_url == request_root_url
        
        def is_separator(self):
            return self.text == '---'
    
    def __init__(self, request):
        self._request_path = request.path
        self._admin_view = request.path.startswith(settings.CENTRAK_ADMIN_PREFIX_URL)
    
    def _get_main_items(self):
        return (
            Menu.Item(self, _('Dashboard'), reverse('home-page')),
            Menu.Item(self, _('Surveys')),
            Menu.Item(self, _('Captures'))
        )
    
    def _get_admin_items(self):
        return (
            Menu.Item(self, _('Dashboard'), reverse('admin-home')),
            Menu.Item(self, _('Organization'), children=(
                Menu.Item(self, _('Info')),
                Menu.Item(self, _('Business Offices')),
                Menu.Item(self, '---'),
                Menu.Item(self, _('Stations')),
                Menu.Item(self, 'Feeeders'))),
            Menu.Item(self, _('Enumeration'), children=(
                Menu.Item(self, _('Projects')),
                Menu.Item(self, _('XForms'), reverse('admin-xforms')))),
        )
    
    @property
    def children(self):
        if not self._admin_view:
            return self._get_main_items()
        return self._get_admin_items()


class ApiClient(object):
    
    def __init__(self, api_url, token=None):
        self.api_url = api_url
        self.token = token
    
    
    
    
    