from django.conf.urls import patterns, url


urlpatterns = patterns('main.views',
    url(r'^$', 'home_page', name='home-page'),
)
