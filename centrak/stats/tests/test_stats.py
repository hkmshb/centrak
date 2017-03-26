import pytest
import pandas as pd
from dolfin.core import Storage
from datetime import date, timedelta

from unittest.mock import MagicMock
from mongoengine import Document, fields

from stats import core as stcore
from core.models import BusinessLevel
from enumeration.models import Capture


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


def make_captures(date, region_infos, counts_list):
    status_list = ['new', 'existing', 'no-supply', 'unknown']
    usr_email, usr_name, counter = 'usr%s@ma.il', 'usr%s', 0
    captures = []

    for (ridx, info) in enumerate(region_infos):
        for (cidx, count) in enumerate(counts_list[ridx]):
            status = status_list[cidx]
            for _ in range(count):
                counter += counter
                Capture.objects.create(date_created=date, date_digitized=date, 
                    user_email=usr_email % counter, cust_name=usr_name % counter, 
                    region_code=info[0], region_name=info[1], acct_status=status)


@pytest.fixture(scope="module")
def level_qs():
    ## mock business level manager
    # setup: create mock objects
    for code, name in [('L1', 'Level1'), ('L2', 'Level2'), ('L3', 'Level3')]:
        MockBusinessLevel.objects.create(code=code, name=name)
    yield MockBusinessLevel.objects

    # teardown: clear database objects
    MockBusinessLevel.objects.delete()


@pytest.fixture
def capture_qs():
    # setup: create objects
    make_captures(date.today(), [('0901', 'KNI')], [(2,0,0,0)])
    make_captures(date.today() + timedelta(days=1),
        [('0901', 'KNI'), ('0903', 'KNE'), ('0902', 'KTC'), ('0908', 'JGS')], 
        [(0,0,1,1), (1,0,0,0), (0,1,0,0), (0,1,0,0)])
    yield Capture.objects
    
    # teardown:
    Capture.objects.delete()


@pytest.fixture
def capture_qs2():
    # setup:
    date_today = date(2017, 2, 7)
    make_captures(date_today, ['KNI','KNC'], [(3,3,4,2), (0,3,2,0)])
    
    date_ystdy = date_today - timedelta(days=1)
    make_captures(date_ystdy, ['KNI', 'KNC'], [(4,2,1,5), (2,3,4,4)])
    
    date_first = date(2017, 2, 1)
    make_captures(date_first, ['KNI', 'KNC'], [(2,5,4,1), (2,4,1,2)])
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
    
    def test_list_of_dict_returned_for_op_with_doc_queryset(self, level_qs):
        qs = level_qs.all()
        out = stcore.queryset_to_values(qs)
        assert isinstance(out, list) == True
        assert out and isinstance(out[0], dict) == True
    
    @pytest.mark.parametrize("fields", [
        ['code'], ['name'], ['code', 'name']])
    def test_op_with_doc_queryset_respects_provided_fields(self, level_qs, fields):
        qs = level_qs.all()
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
    
    def test_dataframe_returned_for_doc_queryset(self, level_qs):
        qs = level_qs.all()
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
    
    def test_single_grouping_accuracy(self, capture_qs):
        result = (('new', 3), ('existing', 2), ('no-supply', 1), 
                  ('unknown', 1), ('_total_', 7))
        
        grouping = ['acct_status']
        out = stcore.stats_count_group_items(capture_qs.all(), *grouping)
        assert out and isinstance(out, Storage)
        assert len(out) == len(result)
        for entry in result:
            assert entry[0] in out \
               and entry[1] == out[entry[0]]
    
    def test_multi_grouping_accuracy(self, capture_qs):
        result = (('JGS', 1), ('KNI', 4), ('KTC', 1), ('KNE', 1), ('_total_', 7))
        grouping = ['region_name', 'acct_status']
        out = stcore.stats_count_group_items(capture_qs.all(), *grouping)
        assert out and isinstance(out, Storage)
        assert len(out) == len(result)
        for entry in result:
            if entry[0] != '_total_':
                assert entry[0] in out \
                   and entry[1] == out[entry[0]]._total_


class TestStatsDashFuncs(object):

    def test_capture_summary_has_four_parts(self, capture_qs):
        df = stcore.queryset_to_dataframe(capture_qs.all())
        st = stcore.stats_dash_capture_summary(df)
        assert st and isinstance(st, Storage) \
           and len(st) == 4 \
           and 'total' in st \
           and 'existing' in st\
           and 'new' in st \
           and 'total:region' in st
    
    def test_capture_summary_accuracy(self, capture_qs):
        df = stcore.queryset_to_dataframe(capture_qs.all())
        st = stcore.stats_dash_capture_summary(df, 'KNI')
        assert st.total == 7 \
           and st.existing == 2 \
           and st.new == 3 \
           and st['total:region'] == 4
    
    def test_capture_analytics_has_two_parts(self, capture_qs):
        df = stcore.queryset_to_dataframe(capture_qs.all())
        st = stcore.stats_dash_capture_analytics(df, date_crnt=date.today())
        assert st and isinstance(st, Storage) \
           and len(st) == 2 \
           and 'ever' in st \
           and 'today' in st
    
    def test_capture_analytics_accuracy(self, capture_qs):
        df = stcore.queryset_to_dataframe(capture_qs.all())
        st = stcore.stats_dash_capture_analytics(df, date_crnt=date.today())
        evr, tdy = st.ever, st.today
        assert tdy.KNI._total_ == 2 
        assert evr['KNI']['_total_'] == 4 and evr['KNI']['new'] == 2 \
           and evr['KNE']['_total_'] == 1 and evr['KNE']['new'] == 1 \
           and evr['KTC']['_total_'] == 1 and evr['KTC']['existing'] == 1 \
           and evr['JGS']['_total_'] == 1 and evr['JGS']['existing'] == 1
    

class TestStatsCapturePaneFuncs(object):

    def test_capture_pane_summary_has_2x4_parts(self, capture_qs2):
        df = stcore.queryset_to_dataframe(capture_qs2.all())
        st = stcore.stats_pane_capture_summary(df, current_region='KNI')
        assert st and isinstance(st, Storage) \
           and len(st) == 2 \
           and 'all' in st  and len(st['all']) == 4 \
           and 'region' in st and len(st['region']) == 4
    
    def test_capture_pane_summary_accuracy(self, capture_qs2):
        df = stcore.queryset_to_dataframe(capture_qs2.all())
        st = stcore.stats_pane_capture_summary(df, curren_region='KNI')
        assert st.all._total_ == 80 \
           and st.all.existing == 25 \
           and st.all.new == 17
        assert st.region.total._total_ == 44 \
           and st.region.total.existing == 12 \
           and st.region.total.new == 11
        assert st.region.today._total_ == 12 \
           and st.region.today.existing == 3 \
           and st.region.today.new == 3
        assert st.region.week._total_ == 28 \
           and st.region.week.existing == 5 \
           and st.region.week.new == 7
        assert st.region.month._total_ == 36 \
           and st.region.month.existing == 10 \
           and st.region.month.new == 9

