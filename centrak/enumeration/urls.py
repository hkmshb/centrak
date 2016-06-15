from django.conf.urls import include, url
from . import views



urlpatterns = [
    # ===+: admin urls
    url(r'^admin/s/',
        include([
            url(r'ntwk/ps/$', views.admin_pstations, name='admin-ntwk-ps'),
        ])),
    
    url(r'^admin/enum/',
        include([
            url(r'xforms/$', views.admin_xforms, name='admin-xforms'),
            url(r'projects/$', views.admin_projects, name='admin-projects')
        ])),
]