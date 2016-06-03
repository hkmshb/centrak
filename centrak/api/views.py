from rest_framework import authentication, permissions
from rest_framework_mongoengine import viewsets
from enumeration.models import XForm

from .serializers import XFormSerializer



class DefaultMixin(object):
    """Default settings for view authentication, permissions,
    filtering and pagination.
    """
    
    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    paginate_by = 25


class XFormViewSet(DefaultMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating XForms."""
    
    queryset = XForm.objects.order_by('object_id')
    serializer_class = XFormSerializer
