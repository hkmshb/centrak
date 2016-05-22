from django.conf.urls import url
from main import views



urlpatterns = [
    
    #: == main urls
    url(r'', views.index, name='home-page'),
]