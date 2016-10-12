from rest_framework import authentication, permissions, filters
from rest_framework import viewsets as drf_viewsets
from rest_framework_mongoengine import viewsets

from core.models import Organization, BusinessOffice
from enumeration.models import Station, PowerLine, Project, XForm

from .forms import BusinessOfficeFilter

from .serializers import StationSerializer, PowerLineSerializer, \
        ProjectSerializer, XFormSerializer, OrganizationSerializer, \
        BusinessOfficeSerializer



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
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )


class StationViewSet(DefaultMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating PowerStations."""
    
    queryset = Station.objects.order_by('object_id')
    serializer_class = StationSerializer


class PowerLineViewSet(DefaultMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating PowerLines."""
    
    queryset = PowerLine.objects.order_by('object_id')
    serializer_class = PowerLineSerializer


class ProjectViewSet(DefaultMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating Projects."""
    
    queryset = Project.objects.order_by('date_started')
    serializer_class = ProjectSerializer


class XFormViewSet(DefaultMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating XForms."""
    
    queryset = XForm.objects.order_by('object_id')
    serializer_class = XFormSerializer


class OrganizationViewSet(DefaultMixin, drf_viewsets.ModelViewSet):
    """API endpoint for listing and creating Orgainzations."""

    queryset =  Organization.objects.order_by('id')
    serializer_class = OrganizationSerializer


class BusinessOfficeViewSet(DefaultMixin, drf_viewsets.ModelViewSet):
    """API endpoint for listing and creating BusinessOffices."""

    queryset = BusinessOffice.objects.order_by('level', 'id')
    serializer_class = BusinessOfficeSerializer
    filter_class = BusinessOfficeFilter
    ordering_fields = ('name', 'code',)

