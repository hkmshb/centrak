from django.contrib.auth import views as auth_views
from django.conf.urls import include, url
from django.conf import settings
from .views import default as def_views
from .views import admin as adm_views



urlpatterns = [
    #: ==+: registration + auth urls 
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
            url('^$', adm_views.admin_home, name='admin-home') ,
            url('^s/org/', adm_views.admin_org, name='admin-org'),
            url('^s/offices/', adm_views.admin_offices, name='admin-offices'),
            
            #: external api services
            url('s/apiservices/{}/$'.format(settings.SURVEY_API_SERVICE_KEY), 
                adm_views.apiservice_survey, name='admin-api-services'),
        ]),
    ),
    
    #: ==+: temp api urls
    url(r'^api/v1/services/survey/token$', adm_views.api_services_set_survey_token,
        name='api-services-survey-token'),
    
    #: ==+: main urls
    url(r'^$', def_views.index, name='home-page'),

    url(r'^projects/', 
        include([
            url(r'^t/$', def_views.projects_list, name='projects-list'),
            
            url(r'^(?P<code>f[0-9A-Fa-f]{3})/',
                include([
                    url(r'^xforms/$', def_views.projects_xform_list, name='projects-xform-list'),
                ])
            )
        ])
    ),
]