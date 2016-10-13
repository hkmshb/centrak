from django.contrib.auth import views as auth_views
from django.conf.urls import include, url
from .views import default as def_views
from .views import admin as adm_views


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
    url(r'admin/',
        include([
            url(r'^$', adm_views.admin_home, name='admin-home'),
        ])
    ),


    #: ==+: main urls
    url(r'^$', def_views.index, name='home-page'),
]
