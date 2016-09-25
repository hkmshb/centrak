from collections import OrderedDict

from django.core.urlresolvers import NoReverseMatch
from django.conf.urls import url

from rest_framework.routers import DefaultRouter as DrfDefaultRouter
from rest_framework_mongoengine.routers import DefaultRouter
from rest_framework import views as drf_views
from rest_framework.response import Response
from rest_framework.reverse import reverse
from . import views


# drf router
router = DrfDefaultRouter()
router.register(r'organizations', views.OrganizationViewSet)
router.register(r'offices', views.BusinessOfficeViewSet)


# drf-mongoengine router
drfm_router = DefaultRouter()
drfm_router.register(r'xforms', views.XFormViewSet)
drfm_router.register(r'projects', views.ProjectViewSet)
drfm_router.register(r'powerlines', views.PowerLineViewSet)
drfm_router.register(r'stations', views.StationViewSet)


api_urls = router.urls[:]
api_urls.extend(drfm_router.urls[2:])



def get_api_root_view():
    """
    Return a view to use as the API root.
    """
    api_root_dict = OrderedDict()
    list_name = router.routes[0].name

    for r in [router, drfm_router]:
        for prefix, viewset, basename in r.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
    
    class APIRoot(drf_views.APIView):

        def get(self, request, *args, **kwargs):
            ret = OrderedDict()
            namespace = request.resolver_match.namespace
            for key, url_name in api_root_dict.items():
                if namespace:
                    url_name = namespace + ':' + url_name
                try:
                    ret[key] = reverse(
                        url_name,
                        args=args,
                        kwargs=kwargs,
                        request=request,
                        format=kwargs.get('format', None)
                    )
                except NoReverseMatch:
                    continue
            return Response(ret)
    return APIRoot.as_view()


api_urls.insert(0, url(r'^$', get_api_root_view()))
