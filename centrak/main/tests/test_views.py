import pytest
from unittest.mock import MagicMock
from django.http import HttpRequest
from django.template.response import TemplateResponse

from main.views import default_views as def_view


class TestIndexView(object):

    def test_response_is_TemplateResponse(self):
        request = MagicMock()
        request.user.is_authenticated = False
        response = def_view.index(request)
        assert isinstance(response, TemplateResponse) == True
    
    def test_response_context_empty_when_logged_out(self):
        request = MagicMock()
        request.user.is_authenticated = False
        response = def_view.index(request)
        context = response.context_data
        assert context != None and len(context) == 0

    def test_response_context_has_stats_data(self):
        request = MagicMock()
        request.user.is_authenticated = True
        response = def_view.index(request)
        context = response.context_data
        assert 'stats' in context \
           and len(context['stats']) == 2 \
           and 'summary' in context['stats'] \
           and 'analytics' in context['stats']
    
    def test_response_summary_stats_adequate_for_dashboard(self):
        request = MagicMock()
        request.user.is_authenticated = True
        response = def_view.index(request)
        stats = response.context_data['stats']['summary']
        valid_entries_found = sum([1 for e in stats if len(e) == 4])
        assert stats and len(stats) == 4 \
           and valid_entries_found == 4
    
    def test_response_analytics_stats_adequate_for_dashboard(self):
        request = MagicMock()
        request.user.is_authenticated = True
        response = def_view.index(request)
        stats = response.context_data['stats']['analytics']
        assert stats and len(stats) == 2
