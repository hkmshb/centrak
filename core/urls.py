from django.conf.urls import patterns, url



urlpatterns = patterns('core.views',
    url(r'^org/info/$', 'org_info', name='org-info'),
    url(r'^org/update$', 'manage_org', name='org-update'),
    url(r'^org/offices/create', 'manage_office', name='office-create'),
    url(r'^org/offices/update/(?P<id>[0-9]+)', 'manage_office',
        name='office-update'),
    url(r'^org/offices/delete(/(?P<id>[0-9]+))?', 'delete_office',
        name='office-delete'),
)
