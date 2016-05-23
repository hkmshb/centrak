from django.contrib.auth import views as auth_views
from django.conf.urls import url
from . import views



urlpatterns = [
    #: ==+: registration + auth urls
    url(r'^account/register', views.register_account, name='register'),
    url(r'^account/registration-complete', views.registration_complete,
        name='registration-complete'),
    url(r'^account/password-reset', views.password_reset,
        name='password-reset'),
    url(r'^account/login', auth_views.login,
        {'template_name':'account/login.html'}, name='login'),
    url(r'^account/logout', auth_views.logout, name='logout'),
    
    #(request, next_page, template_name, redirect_field_name, current_app, extra_context))
    
    #: ==+: main urls
    url(r'', views.index, name='home-page'),
]