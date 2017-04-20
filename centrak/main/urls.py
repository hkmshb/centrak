from django.contrib.auth import views as auth_views
from django.conf.urls import include, url
from .views import default_views as def_views
from .views import admin_views as adm_views
from .views import enum_views as enu_views


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

            url(r'^apiservices/$', adm_views.apiservice_list, name='admin-apiservice-list'),
            url(r'^apiservices/create$', adm_views.manage_apiservice, name='admin-apiservice-add'),
            url(r'^apiservices/(?P<key>\w+)/', include([
                url(r'^$', adm_views.apiservice_detail, name='admin-apiservice-info'),
                url(r'^update$', adm_views.manage_apiservice, name='admin-apiservice-upd'),
                url(r'^set-token$', adm_views.apiservice_detail, name='admin-apiservice-token-set'),
            ])),
            
            url(r'^users/$', adm_views.user_list, name='admin-user-list'),
            url(r'^users/create$', adm_views.manage_user, name='admin-user-add'),
            url(r'^users/(?P<user_id>[0-9]+)/', include([
                url(r'^$', adm_views.user_detail, name='admin-user-info'),
                url(r'^update$', adm_views.manage_user, name='admin-user-upd'),
                url(r'^manage-passwd$', adm_views.user_manage_passwd, name='admin-passwd-set'),
            ])),

            url(r'^offices/', include([
                url(r'^$', adm_views.offices_home, name='admin-offices'),
                url(r'^regions/create$', adm_views.manage_region, 
                    name='admin-region-add'),
                url(r'^regions/(?P<region_code>[0-9]+)/', include([
                    url(r'^update', adm_views.manage_region, name='admin-region-upd'),
                    url(r'^((?P<tab>(stations|powerlines))/)?$',
                        adm_views.region_detail, name='admin-region-info')
                ])),
                
                url(r'^spoints/create$', adm_views.manage_office,
                    name='admin-office-add'),
                url(r'^spoints/(?P<office_code>[0-9]+)/$', adm_views.office_detail,
                    name='admin-office-info'),
                url(r'^spoints/(?P<office_code>[0-9]+)/update$', adm_views.manage_office,
                    name='admin-office-upd'),
            ])),
                
            url(r'^stations/((?P<tab>(transmission|injection|distribution))/)?$', 
                adm_views.powerstation_list, name='admin-station-list'),
            url(r'^powerlines/((?P<tab>(33|11))/)?$', adm_views.powerline_list,
                name='admin-powerline-list'),
            
            url(r'^import/(?P<type>\w+(?:-\w+)?)$', adm_views.manage_imports, name='admin-import'),
        ])
    ),
    
    #: ==+: main urls
    url(r'^$', def_views.index, name='home-page'),
    url(r'^profile/$', def_views.profile_manage_passwd, name='profile-upd'),
    url(r'^notifications/$', def_views.notification_list, name='notification-list'),
    url(r'^notifications/(?P<id>[0-9]+)/$', def_views.notification_detail,
        name='notification-info'),
    url(r'^captures/p/', include([
        url(r'^form/$', enu_views.manage_capture, name='capture-add'),
        url(r'^validate$', enu_views.validate_capture, name='capture-val'),
        url(r'^((?P<tab>new)/)?(?P<ident>\w+)/update$', enu_views.manage_capture, name='capture-upd'),
        url(r'^((?P<tab>new)/)?$', enu_views.capture_index, name='capture-list'),
    ])),
]
