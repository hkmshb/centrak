from django.contrib.auth import views as auth_views
from django.conf.urls import include, url
from .views import default_views as def_views
from .views import admin_views as adm_views


urlpatterns = [
    #: ==+: auth + registration urls
    url(r'^account/register$', def_views.register_account, name='register'),
    url(r'^account/registration-complete/$', def_views.registration_complete,
        name='registration-complete'),
    url(r'^account/password-reset$', def_views.password_reset,
        name='password-reset'),
    url(r'^account/login$', auth_views.login, 
        {'template_name':'account/login.html'}, name='login'),
    url(r'^account/logout$', auth_views.logout, kwargs={'next_page':'home-page'},
        name='logout'),

    
    #: ==+: admin urls
    url(r'^admin/',
        include([
            url(r'^$', adm_views.admin_home, name='admin-home'),
            url(r'^org/$', adm_views.org_info, name='admin-org-detail'),
            url(r'^org/update$', adm_views.manage_org, name='admin-org-upd'),


            url(r'^offices/', include([
                url(r'^$', adm_views.offices_home, name='admin-offices'),

                url(r'^regions/create$', adm_views.manage_region, 
                    name='admin-region-add'),
                url(r'^regions/(?P<region_code>[0-9]+)/(?P<tab>powerlines/)?$', 
                    adm_views.region_detail, name='admin-region-info'),
                url(r'^regions/(?P<region_code>[0-9]+)/update',
                    adm_views.manage_region, name='admin-region-upd'),

                url(r'^spoints/create$', adm_views.manage_office,
                    name='admin-office-add'),
                url(r'^spoints/(?P<office_code>[0-9]+)/$', adm_views.office_detail,
                    name='admin-office-info'),
                url(r'^spoints/(?P<office_code>[0-9]+)/update$', adm_views.manage_office,
                    name='admin-office-upd'),
            ])),
        ])
    ),


    #: ==+: main urls
    url(r'^$', def_views.index, name='home-page'),
]
