from django.conf.urls import patterns, url



urlpatterns = patterns('core.views',
    url(r'^org/info/$', 'org_info', name='org-info'),
    url(r'^org/update$', 'manage_org', name='org-update'),
)
