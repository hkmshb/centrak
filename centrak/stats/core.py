"""
statistics package.
"""
import pandas as pd
from collections import namedtuple
from datetime import date, datetime
from dateutil.relativedelta import *

from dolfin.core import Storage
from django.db.models.query import QuerySet
from mongoengine.queryset import QuerySet as MQuerySet



class DateRange(namedtuple('DateRange', 'start end')):
    __slot__ = ('start', 'end')

    @staticmethod
    def week_from_day(day, firstweekday=0):
        # weekday numbers: mon=0, tue=1, wed=2, thu=3, fri=4, sat=5, sun=6
        if firstweekday not in (MO.weekday, SU.weekday):
            firstweekday = 0
        
        start = day if not hasattr(day, 'date') else day.date()
        if start.weekday() != firstweekday:
            start = start + relativedelta(days=-start.weekday())
        end = start + relativedelta(days=6)
        return DateRange(start, end)

    @staticmethod
    def month_from_day(day):
        day = day if not hasattr(day, 'date') else day.date()
        start = day + relativedelta(month=day.month, day=1)
        end = day + relativedelta(month=start.month, day=32)
        return DateRange(start, end)


def queryset_to_values(qs, *fields):
    # Model QuerySet
    if hasattr(qs, 'values'):
        method = qs.values
        return list(method() if not fields else method(*fields))
    
    # Document QuerySet
    if hasattr(qs, 'only') and hasattr(qs, 'as_pymongo'):
        method = qs.only
        qset = (method() if not fields else method(*fields))
        return list(qset.as_pymongo())
    return None


def queryset_to_dataframe(qs, *fields):
    qs_values = queryset_to_values(qs, *fields)
    if qs_values:
        return pd.DataFrame(qs_values)
    return pd.DataFrame()


def stats_count_group_items(source, *grouping):
    if not isinstance(source, pd.DataFrame):
        source = queryset_to_dataframe(source)
    
    if source.empty or not grouping:
        return Storage({})
    
    found_fields = [f for f in grouping if f in source.columns]
    if len(found_fields) != len(grouping):
        return Storage({})
    
    grouped = source.groupby(grouping)
    series = grouped.size()
    if series.index.nlevels == 1:
        values = Storage(series.items())
        values._total_ = series.sum()
    elif series.index.nlevels > 1:
        values = Storage()
        for key in series.index.levels[0]:
            entry = series[key]
            value = Storage(entry.to_dict())
            value._total_ = entry.sum()
            values[key] = value
        values._total_ = series.sum()
    return values


## DASHBOARD FUNCS

def stats_dash_capture_summary(source, region_code=None):
    if not isinstance(source, pd.DataFrame):
        source = queryset_to_dataframe(source)
    
    result = Storage({'total':0, 'existing':0, 'new':0, 'total:region':0})
    if source.empty:
        return result
    
    counts = stats_count_group_items(source, 'acct_status')
    if not counts:
        return result
    
    # get org wise summaries
    result.total = counts.get('_total_', 0)
    result.existing = counts.get('existing', 0)
    result['new'] = counts.get('new', 0)

    # get region total
    if region_code:
        counts = stats_count_group_items(source, 'region_code')
        if not counts or region_code not in counts:
            return result
        result['total:region'] = counts[region_code]
    return result


def stats_dash_capture_analytics(source, date_crnt=None):
    if not isinstance(source, pd.DataFrame):
        source = queryset_to_dataframe(source)
    
    result = Storage({'ever':Storage(), 'today':Storage()})
    if source.empty:
        return result
    
    # calculate stats for ever
    grouping = ['region_code', 'acct_status']
    counts = stats_count_group_items(source, *grouping)
    result.ever = Storage(counts)

    # calculate stats for today
    if not date_crnt:
        date_crnt = date.today()
    grouping = ['region_code', 'acct_status']
    df = source[source['date_created'] == date_crnt]
    counts = stats_count_group_items(df, *grouping)
    result.today = Storage(counts)
    return result


def stats_pane_capture_summary(user, source, date_crnt=None):
    perc = lambda p,t: '%.0f' % (((p or 0)/(t or 1)) * 100)

    def _summaries(df):
        key, count = 'acct_status', Storage({'existing':0, 'new':0, 'total':0})
        tmp = stats_count_group_items(df, key)
        if 'user_email' in df.columns:
            dft = df[df['user_email'] == user.username]
            count = stats_count_group_items(dft, key)
        count.perc = perc(count._total_, tmp._total_)
        count.total = count._total_     # adjusted for use in tmpl
        count.region = tmp._total_
        return count

    if not isinstance(source, pd.DataFrame):
        source = queryset_to_dataframe(source)

    stats = Storage(summary=[])
    tdy = date_crnt if date_crnt else date.today()
    periods = (('total', None), ('day', (tdy,)),
               ('week', DateRange.week_from_day(tdy)),
               ('month', DateRange.month_from_day(tdy)))
    
    for (label, bound) in periods:
        if bound is None:
            stats.summary.append((label, _summaries(source)))
        elif 'date_created' in source.columns:
            fmt_dt = '%Y-%m-%d'
            if len(bound) == 1:
                df = source[source['date_created'] == bound[0].strftime(fmt_dt)]
                stats.summary.append(('this %s' % label, _summaries(df)))
            else:
                df = source[source['date_created'] >= bound[0].strftime(fmt_dt)]
                df = df[df['date_created'] <= bound[1].strftime(fmt_dt)]
                stats.summary.append(('this %s' % label, _summaries(df)))
        else:
            stats.summary.append(('this %s' % label, Storage()))
    return stats


def stats_pane_capture_history(user, model):
    pipeline = [
        {'$match': {'user_email': user.username}},
        {'$group': {'_id':'$date_digitized', 'total':{'$sum': 1}}},
        {'$sort': {'_id': -1}},
        {'$limit': 10}
    ]
    query = model.objects.aggregate(*pipeline)
    return [(r['_id'], r['total']) for r in query]
