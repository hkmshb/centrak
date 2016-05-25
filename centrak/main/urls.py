from django.contrib.auth import views as auth_views
from django.conf.urls import url
from . import views



urlpatterns = [
    #: ==+: registration + auth urls
    url(r'^account/register', views.register_account, name='register'),
    url(r'^account/registration-complete/', views.registration_complete,
        name='registration-complete'),
    url(r'^account/password-reset', views.password_reset,
        name='password-reset'),
    url(r'^account/login', auth_views.login,
        {'template_name':'account/login.html'}, name='login'),
    url(r'^account/logout', auth_views.logout, kwargs={'next_page':'home-page'}, 
        name='logout'),
    
    
    #: ==+: admin urls
    url(r'^admin/', views.admin_home, name='admin-home'),
    
    
    #: ==+: main urls
    url(r'', views.index, name='home-page'),
    
]