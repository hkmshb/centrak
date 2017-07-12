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


def make_captures(date, region_infos, counts_list, email=None):
    print('input: %s' % [date, region_infos, counts_list, email])
    status_list = ['new', 'existing', 'no-supply', 'unknown']
    usr_email, usr_name, counter = 'usr%s@ma.il', 'usr%s', 0
    captures = []

    dt = date if not hasattr(date, 'date') else date.date()
    for (ridx, info) in enumerate(region_infos):
        for (cidx, count) in enumerate(counts_list[ridx]):
            status = status_list[cidx]
            for _ in range(count):
                counter += counter
                Capture.objects.create(
                    date_created=dt, date_digitized=dt,
                    cust_name=usr_name % counter, region_code=info[0], 
                    region_name=info[1], acct_status=status,
                    user_email= email or usr_email % counter,
                    medium=Capture.MEDIUM_PAPER
                )


def make_test_pack():
    dy, wk = date.today(), date.today() - timedelta(days=8)
    mt = dy - timedelta(days=dy.day + 7)
    countlist, batches = [3, 2, 1, 0], [
        ('abdulhakeem.shaibu@kedco.ng', ('KNI', 'KN Industrial')),
        ('abdulrahman.shehu@kedco.ng', ('KNI', 'KN Industrial')),
        ('itdevelop@kedco.ng', ('JIS', 'JI South')),
        ('itdevelop@kedco.ng', ('JIN', 'JI North'))
    ]
    for username, region in batches:
        for dt in (dy, wk, mt):
            make_captures(dt, [region], [countlist], username)
            countlist = countlist[-1:] + countlist[:-1]


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
    # empty existing data
    Capture.objects.delete()

    # setup: create objects
    # note: the counts list eg (2,0,0,0) rep (new,existing,no-supply,unknown)
    # to be created ...
    make_captures(date.today(), [('KNI', 'KN Industrial')], [(2,0,0,0)])
    make_captures(date.today() + timedelta(days=1),
        [('KNI', 'KN Industrial'), ('KNE', 'KN East'), 
         ('KTC', 'KT Central'), ('JGS', 'JG South')], 
        [(0,0,1,1), (1,0,0,0), (0,1,0,0), (0,1,0,0)])
    yield Capture.objects
    
    # teardown:
    Capture.objects.delete()


@pytest.fixture
def capture_qs2():
    # clear existing data
    Capture.objects.delete()

    # setup:
    date_today = date(2017, 2, 7)
    make_captures(date_today, [('KNI', 'KN Industrial'),('KNC', 'KN Central')], 
                  [(3,3,4,2), (0,3,2,0)])
    
    date_ystdy = date_today - timedelta(days=1)
    make_captures(date_ystdy, [('KNI', 'KN Industrial'), ('KNC', 'KN Central')], 
                  [(4,2,1,5), (2,3,4,4)])
    
    date_first = date(2017, 2, 1)
    make_captures(date_first, [('KNI', 'KN Industrial'), ('KNC', 'KN Central')], 
                  [(2,5,4,1), (2,4,1,2)])
    yield Capture.objects

    # teardown:
    Capture.objects.delete()


class TestDateRange(object):
    pass

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
        result = (('JG South', 1), ('KN Industrial', 4), ('KT Central', 1),
                  ('KN East', 1), ('_total_', 7))
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
        # mock user
        user = MagicMock()
        user.username = 'usr0@ma.il'

        # filter down to KNI
        source = capture_qs2(region_code='KNI').all()
        df = stcore.queryset_to_dataframe(source)
        st = stcore.stats_pane_capture_summary(user, df, date(2017, 2, 7))

        assert st and isinstance(st, Storage)
        assert len(st) == 1 and 'summary' in st
        assert 'total' in st.summary[0]
        assert 'this day' in st.summary[1]
        assert 'this week' in st.summary[2]
        assert 'this month' in st.summary[3]
    
    def test_capture_pane_summary_accuracy(self, capture_qs2):
        # mock user
        user = MagicMock()
        user.username = 'usr0@ma.il'

        # filter down to KNI
        source = capture_qs2(region_code='KNI').all()
        df = stcore.queryset_to_dataframe(source)
        st = stcore.stats_pane_capture_summary(user, df, date(2017, 2, 7))
        
        stat = st.summary[0][1]
        assert stat.total == 36
        assert stat.new == 9
        assert stat.existing == 10
        assert stat.unknown == 8

        stat = st.summary[1][1]
        assert stat.total == 12
        assert stat.new == 3
        assert stat.existing == 3
        assert stat.unknown == 2

        stat = st.summary[2][1]
        assert stat.total == 24
        assert stat.new == 7
        assert stat.existing == 5
        assert stat.unknown == 7

        stat = st.summary[3][1]
        assert stat.total == 36
        assert stat.new == 9
        assert stat.existing == 10
        assert stat.unknown == 8
