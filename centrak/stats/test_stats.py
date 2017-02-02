import pytest
import pandas as pd
from dolfin.core import Storage
from datetime import date, timedelta

from unittest.mock import MagicMock
from mongoengine import Document, fields

from stats import core as stcore
from core.models import BusinessLevel



class MockDocQuerySet(object):
    def only(self, *fields):
        pass


class MockBusinessLevel(Document):
    code = fields.StringField(max_length=2, choices=BusinessLevel.LEVEL_CHOICES)
    name = fields.StringField(max_length=20)
    
    meta = {
        'collection': 'business_level'
    }
    
    def __str__(self):
        return self.name


@pytest.fixture(scope="module")
def bl_objects():
    ## mock business level manager
    # setup: create mock objects
    for code, name in [('L1', 'Level1'), ('L2', 'Level2'), ('L3', 'Level3')]:
        MockBusinessLevel.objects.create(code=code, name=name)
    yield MockBusinessLevel.objects

    # teardown: clear database objects
    MockBusinessLevel.objects.delete()


@pytest.fixture
def capture_objects():
    from enumeration.models import Capture
    
    # setup: create objects1
    name, email = ('usr', 'usr@abc.ng')
    today = date.today()
    tmrw = today + timedelta(days=1)
    captures = [
        {'date_created': today, 'user_email':email, 'cust_name':name, 'region_name':'KNI', 'acct_status':'new'},
        {'date_created': today, 'user_email':email, 'cust_name':name, 'region_name':'KNI', 'acct_status':'new'},
        {'date_created': tmrw, 'user_email':email, 'cust_name':name, 'region_name':'KNI', 'acct_status':'no-supply'},
        {'date_created': tmrw, 'user_email':email, 'cust_name':name, 'region_name':'KNI', 'acct_status':'unknown'},
        {'date_created': tmrw, 'user_email':email, 'cust_name':name, 'region_name':'KNE', 'acct_status':'new'},
        {'date_created': tmrw, 'user_email':email, 'cust_name':name, 'region_name':'KTC', 'acct_status':'existing'},
        {'date_created': tmrw, 'user_email':email, 'cust_name':name, 'region_name':'JGS', 'acct_status':'existing'}]
    for capture in captures:
        Capture.objects.create(**capture)
    yield Capture.objects

    # teardown:
    Capture.objects.delete()


@pytest.mark.django_db
class TestQuerySetToValues(object):
    
    def test_None_returned_for_invalid_object(self):
        qs = stcore.queryset_to_values(object())
        assert qs == None
    
    def test_None_returned_for_invalid_doc_queryset_interface(self):
        qs = stcore.queryset_to_values(MockDocQuerySet())
        assert qs == None
    
    ## Model Objects
    def test_calls_values_func_on_model_queryset(self):
        qs = MagicMock(spec=BusinessLevel.objects)
        out = stcore.queryset_to_values(qs)
        qs.values.assert_called_once_with()
    
    def test_list_of_dict_return_for_op_with_model_queryset(self):
        qs = BusinessLevel.objects.all()
        out = stcore.queryset_to_values(qs)
        assert isinstance(out, list) == True
        assert out and isinstance(out[0], dict) == True
    
    @pytest.mark.parametrize("fields", [
        ['code'], ['name'], ['code', 'name']])
    def test_op_with_model_queryset_respects_provided_fields(self, fields):
        qs = BusinessLevel.objects.all()
        out = stcore.queryset_to_values(qs, *fields)
        assert out and len(out[0].keys()) == len(fields)
    
    ## Document Objects
    def test_calls_only_func_on_doc_queryset(self):
        qs = MagicMock(spec=MockBusinessLevel.objects)
        out = stcore.queryset_to_values(qs)
        qs.only.assert_called_once_with()
    
    def test_list_of_dict_returned_for_op_with_doc_queryset(self, bl_objects):
        qs = bl_objects.all()
        out = stcore.queryset_to_values(qs)
        assert isinstance(out, list) == True
        assert out and isinstance(out[0], dict) == True
    
    @pytest.mark.parametrize("fields", [
        ['code'], ['name'], ['code', 'name']])
    def test_op_with_doc_queryset_respects_provided_fields(self, bl_objects, fields):
        qs = bl_objects.all()
        out = stcore.queryset_to_values(qs, *fields)
        assert out and len(out[0].keys()) == len(fields)


class TestQuerySetToDataFrame(object):

    @pytest.mark.parametrize("obj", [None, object()])
    def test_empty_dataframe_returned_for_None_or_invalid_object(self, obj):
        df = stcore.queryset_to_dataframe(obj)
        assert isinstance(df, pd.DataFrame) \
           and df.empty == True
    
    @pytest.mark.django_db
    def test_dataframe_returned_for_model_queryset(self):
        qs = BusinessLevel.objects.all()
        df = stcore.queryset_to_dataframe(qs)
        assert isinstance(df, pd.DataFrame) \
           and df.empty == False \
           and len(df.index) == 3
    
    def test_dataframe_returned_for_doc_queryset(self, bl_objects):
        qs = bl_objects.all()
        df = stcore.queryset_to_dataframe(qs)
        assert isinstance(df, pd.DataFrame) \
           and df.empty == False \
           and len(df.index) == 3


class TestStatsCountGroupItems(object):
    
    def test_returns_empty_dict_for_empty_dataframe(self):
        out = stcore.stats_count_group_items(pd.DataFrame(), 'code')
        assert out != None and len(out) == 0 \
           and isinstance(out, Storage)
    
    @pytest.mark.django_db
    def test_returns_empty_dict_for_invalid_column(self):
        qs = BusinessLevel.objects.all()
        df = stcore.queryset_to_dataframe(qs)
        out = stcore.stats_count_group_items(df, 'k0d3')
        assert out != None and isinstance(out, Storage) \
           and len(out) == 0
    
    def test_single_grouping_accuracy(self, capture_objects):
        result = (('new', 3), ('existing', 2), ('no-supply', 1), 
                  ('unknown', 1), ('_total_', 7))
        
        grouping = ['acct_status']
        out = stcore.stats_count_group_items(capture_objects.all(), *grouping)
        assert out and isinstance(out, Storage)
        assert len(out) == len(result)
        for entry in result:
            assert entry[0] in out \
               and entry[1] == out[entry[0]]
    
    def test_multi_grouping_accuracy(self, capture_objects):
        result = (('JGS', 1), ('KNI', 4), ('KTC', 1), ('KNE', 1), ('_total_', 7))
        grouping = ['region_name', 'acct_status']
        out = stcore.stats_count_group_items(capture_objects.all(), *grouping)
        assert out and isinstance(out, Storage)
        assert len(out) == len(result)
        for entry in result:
            if entry[0] != '_total_':
                assert entry[0] in out \
                   and entry[1] == out[entry[0]]._total_


class TestStatsDashFuncs(object):

    def test_capture_summary_has_four_parts(self, capture_objects):
        df = stcore.queryset_to_dataframe(capture_objects.all())
        st = stcore.stats_dash_capture_summary(df)
        assert st and isinstance(st, Storage) \
           and len(st) == 4 \
           and 'total' in st \
           and 'existing' in st\
           and 'new' in st \
           and 'total:region' in st
    
    def test_capture_summary_accuracy(self, capture_objects):
        df = stcore.queryset_to_dataframe(capture_objects.all())
        st = stcore.stats_dash_capture_summary(df, 'KNI')
        assert st.total == 7 \
           and st.existing == 2 \
           and st.new == 3 \
           and st['total:region'] == 4
    
    def test_capture_analytics_has_two_parts(self, capture_objects):
        df = stcore.queryset_to_dataframe(capture_objects.all())
        st = stcore.stats_dash_capture_analytics(df, date_crnt=date.today())
        assert st and isinstance(st, Storage) \
           and len(st) == 2 \
           and 'ever' in st \
           and 'today' in st
    
    def test_capture_analytics_accuracy(self, capture_objects):
        df = stcore.queryset_to_dataframe(capture_objects.all())
        st = stcore.stats_dash_capture_analytics(df, date_crnt=date.today())
        evr, tdy = st.ever, st.today
        assert tdy.KNI._total_ == 2 
        assert evr['KNI']['_total_'] == 4 and evr['KNI']['new'] == 2 \
           and evr['KNE']['_total_'] == 1 and evr['KNE']['new'] == 1 \
           and evr['KTC']['_total_'] == 1 and evr['KTC']['existing'] == 1 \
           and evr['JGS']['_total_'] == 1 and evr['JGS']['existing'] == 1
    
