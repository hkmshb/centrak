import pytest
from unittest.mock import MagicMock
from django.http import HttpRequest
from django.template.response import TemplateResponse

from main.views import default_views as def_views
from main.views import enum_views


@pytest.fixture
def auth_request():
    request = MagicMock()
    request.user.is_authenticated.return_value = True
    return request


class TestIndexView(object):

    def test_response_is_TemplateResponse(self):
        request = MagicMock()
        request.user.is_authenticated = False
        response = def_views.index(request)
        assert isinstance(response, TemplateResponse) == True
    
    def test_response_context_empty_when_logged_out(self):
        request = MagicMock()
        request.user.is_authenticated = False
        response = def_views.index(request)
        context = response.context_data
        assert context != None and len(context) == 0

    def test_response_context_has_stats_data(self, auth_request):
        response = def_views.index(auth_request)
        context = response.context_data
        assert 'stats' in context \
           and len(context['stats']) == 2 \
           and 'summary' in context['stats'] \
           and 'analytics' in context['stats']
    
    def test_response_summary_stats_adequate_for_dashboard(self, auth_request):
        response = def_views.index(auth_request)
        stats = response.context_data['stats']['summary']
        valid_entries_found = sum([1 for e in stats if len(e) == 4])
        assert stats and len(stats) == 4 \
           and valid_entries_found == 4
    
    def test_response_analytics_stats_adequate_for_dashboard(sel, auth_request):
        response = def_views.index(auth_request)
        stats = response.context_data['stats']['analytics']
        assert stats and len(stats) == 2


class TestCaptureView(object):

    def test_only_authenticated_access_permitted(self):
        request = MagicMock()
        request.user.is_authenticated.return_value = False
        
        # hint: mock below required for django.contrib.auth.login_required
        request.build_absolute_uri.return_value = 'http://localhost/captures/p/'
        response = enum_views.capture_index(request)
        assert response.status_code == 302 \
           and response.url.startswith('/account/login')
    
    def test_response_context_has_stats_data(self, auth_request):
        response = enum_views.capture_index(auth_request)
        context = response.context_data
        assert 'stats' in context \
           and len(context['stats']) == 2 \
           and 'summary' in context['stats'] \
           and 'history' in context['stats']
    
    def test_response_summary_stats_adequate_for_side_pane(self, auth_request):
        response = enum_views.capture_index(auth_request)
        stats = response.context_data['stats']['summary']
        valid_entries_found = sum([1 for e in stats if len(e) == 4])
        assert stats and len(stats) == 4 \
           and valid_entries_found == 4
    
    def test_response_history_stats_adequate_for_side_pane(self, auth_request):
        response = enum_views.capture_index(auth_request)
        stats = response.context_data['stats']['history']
        assert stats and len(stats) >= 2
    