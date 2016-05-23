from django.contrib.auth import views as auth_views
from django.conf.urls import url
from . import views



urlpatterns = [
    #: ==+: registration + auth urls
    url(r'^account/register', views.register_account, name='register'),
    url(r'^account/registration-complete', views.registration_complete,
        name='registration-complete'),
    
    #: ==+: main urls
    url(r'', views.index, name='home-page'),
]