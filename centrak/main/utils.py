from collections import namedtuple

from django.utils.translation import ugettext_lazy as _
from django.utils.functional import SimpleLazyObject
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.conf import settings



#: helper functions
def is_admin_view(request):
    target_prefix = settings.CENTRAK_ADMIN_PREFIX_URL.lower()
    return (request.path.lower().startswith(target_prefix))


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
            
            if self.children:
                request_root_url = self.menu._request_path.split('/')[1:3]
                item_root_url = item_url.split('/')[1:3]
                return item_root_url == request_root_url
            else:
                return self.url == self.menu._request_path
        
        def is_separator(self):
            return self.text == '---'
    
    def __init__(self, request):
        self._request_path = request.path
        self._admin_view = request.path.startswith(settings.CENTRAK_ADMIN_PREFIX_URL)
    
    def _get_main_items(self):
        return (
            Menu.Item(self, _('Dashboard'), reverse('home-page')),
            Menu.Item(self, _('Projects'), reverse('projects-list')),
            Menu.Item(self, _('Captures'))
        )
    
    def _get_admin_items(self):
        return (
            Menu.Item(self, _('Dashboard'), reverse('admin-home')),
            Menu.Item(self, _('Settings'), '/admin/s/', children=(
                Menu.Item(self, _('Organisation'), reverse('admin-org')),
                Menu.Item(self, _('Business Offices'), reverse('admin-offices')),
                Menu.Item(self, '---'),
                Menu.Item(self, _('Power Stations'), reverse('admin-ntwk-ps')),
                Menu.Item(self, _('Power Lines (Feeders)')),
                Menu.Item(self, _('Distribution Stations')),
                Menu.Item(self, '---'),
                Menu.Item(self, _('External API Services'), reverse('admin-api-services')))),
            Menu.Item(self, _('Enumeration'), '/admin/enum/', children=(
                Menu.Item(self, _('Projects'), reverse('admin-projects')),
                Menu.Item(self, _('XForms'), reverse('admin-xforms')))),
        )
    
    @property
    def children(self):
        if not self._admin_view:
            return self._get_main_items()
        return self._get_admin_items()

