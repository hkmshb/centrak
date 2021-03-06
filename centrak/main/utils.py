import re
from collections import namedtuple

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings



# string consts ::
MSG_FMT_SUCCESS_ADD = '%s added successfully.'
MSG_FMT_SUCCESS_UPD = '%s updated successfully.'

# pattern consts ::
PATTERN_ACCT1 = r'\d{2}/\d{2}/\d{2}/\d{4}-01'
PATTERN_ACCT2 = r'\d{10}-01'
PATTERN_MTRNO = r'\d{11}'


def is_acct_no(value):
    return re.match(PATTERN_ACCT1, value) is not None \
        or re.match(PATTERN_ACCT2, value) is not None


def is_meter_no(value):
    return re.match(PATTERN_MTRNO, value) is not None


def expand_acct_no(acct_no):
    if re.match(PATTERN_ACCT2, acct_no):
        chunks = (acct_no[:2], acct_no[2:4], acct_no[4:6], acct_no[6:])
        return "%s/%s/%s/%s" % chunks
    return acct_no


##:: menu
def is_admin_view(request):
    target_prefix = settings.CENTRAK_ADMIN_PREFIX_URL.lower()
    return (request.path.lower().startswith(target_prefix))


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
            Menu.Item(self, _('Captures'), 'fa-database', reverse('capture-list')),
        )
    
    def _get_admin_items(self):
        return (
            Menu.Item(self, _('Dashboard'), 'fa-dashboard', reverse('admin-home')),
            Menu.Item(self, _('Projects'), 'fa-cubes'),
            Menu.Item(self, _('Survey XForms'), 'fa-wpforms', reverse('admin-xform-list')),
            Menu.Item(self, _('Customers'), 'fa-users', children=(
                Menu.Item(self, _('Accounts'), 'fa-book', reverse('admin-acct-list')),
                Menu.Item(self, _('Payments'), 'fa-money'))),
            Menu.Item(self, _('System'), 'fa-gears', children=(
                Menu.Item(self, _('Settings'), 'fa-gears'),
                Menu.Item(self, _('Users'), 'fa-users', reverse('admin-user-list')),
                Menu.Item(self, _('External API Services'), 'fa-cloud', reverse('admin-apiservice-list')))),
            Menu.Item(self, _('DISCO Setup'), 'fa-institution', children=(
                Menu.Item(self, _('Organisation'), 'fa-building-o', reverse('admin-org-detail')),
                Menu.Item(self, _('Business Offices'), 'fa-home', reverse('admin-offices')),
                Menu.Item(self, '---'),
                Menu.Item(self, _('Network Stations'), 'fa-shield fa-flip-horizontal', reverse('admin-station-list')),
                Menu.Item(self, _('Powerlines (Feeders)'), 'fa-flash', reverse('admin-powerline-list')))),
        )
    
    @property
    def children(self):
        if not self._admin_view:
            return self._get_main_items()
        return self._get_admin_items()
    
    @property
    def is_admin_view(self):
        return self._admin_view

