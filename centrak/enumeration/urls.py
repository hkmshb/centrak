from django.conf.urls import include, url
from . import views



urlpatterns = [
    url(r'^admin/', include([
        url(r'^xforms/((?P<tab>(imported|external))/)?', include([
            url(r'^$', views.xform_list, name='admin-xform-list'),
        ])),
    ])),
]
