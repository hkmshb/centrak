from django.conf.urls import include, url
from . import views



urlpatterns = [
    # ===+: admin urls
    url(r'^admin/enum/',
        include([
            url(r'xforms/$', views.xforms_list, name='admin-xforms'),
            url(r'ntwk/ps/$', views.network_ps, name='admin-ntwk-ps'),
        ])),
]