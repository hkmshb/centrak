from collections import OrderedDict

from django.core.urlresolvers import NoReverseMatch
from django.conf.urls import url

from rest_framework_mongoengine.routers import DefaultRouter as MDefaultRouter
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from . import views


# drf routes
router = DefaultRouter()
router.register('apiservices', views.ApiServiceInfoViewSet)


# drf-m routes
mrouter = MDefaultRouter()
mrouter.register('xforms', views.XFormViewSet)


api_urls = router.urls[:]
api_urls.extend(mrouter.urls[:])

def get_api_root_view():
    """
    Returns a view to use as the API root.
    """
    api_root_dict = OrderedDict()
    list_name = router.routes[0].name

    for r in [router, mrouter]:
        for prefix, viewset, basename in r.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
    
    class APIRoot(APIView):

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
