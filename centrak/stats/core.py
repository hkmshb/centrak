"""
statistics package.
"""
import pandas as pd
from datetime import date
from dolfin.core import Storage
from django.db.models.query import QuerySet
from mongoengine.queryset import QuerySet as MQuerySet



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
    
    # else
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

def stats_dash_capture_summary(source, region_name=None):
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
    if region_name:
        counts = stats_count_group_items(source, 'region_name')
        if not counts or region_name not in counts:
            return result
        result['total:region'] = counts[region_name]
    return result


def stats_dash_capture_analytics(source, date_crnt=None):
    if not isinstance(source, pd.DataFrame):
        source = queryset_to_dataframe(source)
    
    result = Storage({'ever':Storage(), 'today':Storage()})
    if source.empty:
        return result
    
    # calculate stats for ever
    grouping = ['region_name', 'acct_status']
    counts = stats_count_group_items(source, *grouping)
    result.ever = Storage(counts)

    # calculate stats for today
    if not date_crnt:
        date_crnt = date.today()
    grouping = ['region_name', 'acct_status']
    df = source[source['date_created'] == date_crnt]
    counts = stats_count_group_items(df, *grouping)
    result.today = Storage(counts)
    return result


def stats_pane_capture_summary(source, region_name, date_crnt):
    if not isinstance(source, pd.DataFrame):
        source = queryset_to_dataframe(source)
    
    result = Storage({'all':Storage(), 'region':Storage()})
    if source.empty:
        return result
    
    # calculate stats for all
    counts = stats_count_group_items(df, ['acct_status'])
    result.all.update(counts)

    ## calculate stats for region
    # total
    df2 = df[df['region_name'] == region_name]
    counts = stats_count_group_items(df2, ['acct_status'])
    result.region.total = counts

    # month
    if not date_crnt: date_crnt = date.today()
    date_first = date_crnt.replace(day=1)
    date_last = date_crnt.replace(day=31)


def stats_pane_capture_history(source, region_name):
    pass
