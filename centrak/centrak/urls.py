"""centrak URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from rest_framework.authtoken.views import obtain_auth_token
from api.urls import api_urls



urlpatterns = [
    url(r'^su:admin/', include(admin.site.urls)),
    url(r'^api/token/', obtain_auth_token, name='api-token'),
    url(r'api/v1/', include(api_urls)),
    url(r'session_security', include('session_security.urls')),
    url(r'', include('enumeration.urls')),
    url(r'', include('main.urls')),
]


#: custom error pages
handler400 = 'main.views.default_views.handle_bad_request'
handler403 = 'main.views.default_views.handle_access_denied'
handler404 = 'main.views.default_views.handle_not_found'
handler500 = 'main.views.default_views.handle_server_error'


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ]

    # included for viewing ease during page design
    urlpatterns += [
        url(r'400/', 'main.views.default_views.handle_bad_request'),
        url(r'403/', 'main.views.default_views.handle_access_denied'),
        url(r'404/', 'main.views.default_views.handle_not_found'),
        url(r'500/', 'main.views.default_views.handle_server_error'),
    ]
