from rest_framework import authentication, permissions, filters
from rest_framework import viewsets
from rest_framework_mongoengine import viewsets as mviewsets

from core.models import ApiServiceInfo
from enumeration.models import XForm
from .serializers import ApiServiceInfoSerializer, XFormSerializer



class DefaultMixin(object):
    """
    Default settings for view authentication, permissions, filtering and pagination.
    """
    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )
    paginate_by_param = 'pageSize'
    max_paginate_by = 100
    paginate_by = 25
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )


class ApiServiceInfoViewSet(DefaultMixin, viewsets.ModelViewSet):
    """
    API endpoint for listing and managing ApiServiceInfo objects.
    """
    queryset = ApiServiceInfo.objects.order_by('date_created')
    serializer_class = ApiServiceInfoSerializer


class XFormViewSet(DefaultMixin, mviewsets.ModelViewSet):
    """
    API endpoint for listing and creating XForms.
    """
    queryset = XForm.objects.order_by('object_id')
    serializer_class = XFormSerializer

