from django.conf.urls import patterns, url


urlpatterns = patterns('enumeration.views',
    url(r'^device-options/manufacturers/$', 'manufacturers', 
        name='manufacturers'),
)
