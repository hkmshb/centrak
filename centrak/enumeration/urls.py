from django.conf.urls import include, url
from . import views



urlpatterns = [
    url(r'^admin/', include([
        url(r'^xforms/', include([
            url(r'^((?P<tab>(imported|external))/)?$', views.xform_list, name='admin-xform-list'),
            url(r'^(?P<object_id>[0-9]+)/$', views.xform_detail, name='admin-xform-info'),
            url(r'^(?P<object_id>[0-9]+)/update$', views.manage_xform, name='admin-xform-upd'),
        ])),
        url(r'^accounts/$', views.accounts_list, name='admin-acct-list'),
    ])),
]
