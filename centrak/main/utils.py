from collections import namedtuple

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings



# string const ::
MSG_FMT_SUCCESS_ADD = '%s added successfully.'
MSG_FMT_SUCCESS_UPD = '%s updated successfully.'


##::
class Menu(object):
    """Defines the application menu."""
    
    class Item(namedtuple('Item', ['menu', 'text', 'icon', 'url', 'children'])):
        
        def __new__(cls, menu, text, icon=None, url=None, children=None):
            kwargs = {'menu': menu, 'text': text, 'icon': icon or '', 
                      'url': url or '', 'children': children or []}
            item = super(Menu.Item, cls).__new__(cls, **kwargs)
            return item
        
        def is_active(self):
            default_if_none_url = '_/_'
            item_url = self.url or default_if_none_url
            
            if self.children or self.menu._admin_view:
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
            Menu.Item(self, _('Dashboard'), 'fa-dashboard', reverse('home-page')),
            Menu.Item(self, _('Projects'), 'fa-cubes'),
            Menu.Item(self, _('Captures'), 'fa-clone')
        )
    
    def _get_admin_items(self):
        return (
            Menu.Item(self, _('Dashboard'), 'fa-dashboard', reverse('admin-home')),
            Menu.Item(self, _('Projects'), 'fa-cubes'),
            Menu.Item(self, _('Survey Forms'), 'fa-wpforms'),
            Menu.Item(self, _('System'), 'fa-gears', '/admin/system/', children=(
                Menu.Item(self, _('Settings'), 'fa-gears'),
                Menu.Item(self, _('Users'), 'fa-users'),
                Menu.Item(self, _('External API Services'), 'fa-cloud'))),
            Menu.Item(self, _('DISCO Setup'), 'fa-institution', children=(
                Menu.Item(self, _('Organisation'), 'fa-building-o', reverse('admin-org-detail')),
                Menu.Item(self, _('Business Offices'), 'fa-home'),
                Menu.Item(self, '---'),
                Menu.Item(self, _('Power Stations'), 'fa-shield fa-flip-horizontal'),
                Menu.Item(self, _('Powerlines (Feeders)'), 'fa-flash'),
                Menu.Item(self, _('Distribution Stations'), 'fa-adjust'))),
        )
    
    @property
    def children(self):
        if not self._admin_view:
            return self._get_main_items()
        return self._get_admin_items()
    
    @property
    def is_admin_view(self):
        return self._admin_view

