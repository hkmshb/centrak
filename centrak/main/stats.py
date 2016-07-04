import pandas as pd
from datetime import datetime

from mongoengine.queryset import Q

from core.utils import Storage
from core.models import Stats, StatsBatch
from enumeration.models import SyncLog, XForm, Capture, Update



VALUES_ACCT_STATUS = ('ytbd','new','existing','no-supply')
VALUES_METER_TYPE  = ('none','analogue','ppm')



def for_project(project, key, rebuild=False):
    pure_count = Capture.objects(project_id__startswith=project.code).count()
    blank_stats = _get_blank_stats_entry()
    fstats = Stats.objects(key=key).first() or blank_stats
    if not rebuild and pure_count == fstats.count:
        return fstats 
    
    _build_stats_for_project(project, key, rebuild)
    return Stats.objects(key=key).first() or blank_stats


def for_project_xform(xform, key, rebuild=False):
    """
    * get capture count by xform id_string
    * get stat for xform id_string and compare counts
    * if counts equal, return stat
    * update stat
        * pull recently added captures; use pulled count to compare main count
        * if counts equal, summaries captures by date of capture and update stats
        * if not equal summarize entire captures; per day then for all 
    """
    # excluded dropped objects in count
    _xform_qs = Q(_xform_id_string=xform.id_string)
    update_qs = (Q(dropped=False) | Q(dropped=False) & Q(merged=False))
    
    survey_class, main_qs = (Capture, (_xform_qs & Q(dropped=False)))
    if xform.type == xform.TYPE_UPDATE:
        survey_class = Update
        main_qs = _xform_qs & update_qs
    
    pure_count = survey_class.objects(main_qs).count()
    blank_stats = _get_blank_stats_entry()
    fstats = Stats.objects(key=key).first() or blank_stats
    if not rebuild and pure_count == fstats.count:
        return fstats
    
    _build_stats_for_project_xform(survey_class, main_qs, fstats, pure_count,
                                   xform, key, rebuild)
    return Stats.objects(key=key).first() or blank_stats


def _build_stats_for_project(project, key, rebuild):
    form_keys = []
    for xform in XForm.objects(id_string__in=project.xforms):
        form_key = "{}.form.{}".format(key, xform.id_string)
        _build_stats_for_project_xform(xform, form_key, rebuild)
        form_keys.append(form_key)
    
    columns = _get_blank_stats_entry().keys()
    records = Stats.objects(key__in=form_keys).only(*columns)
    df = pd.read_json(records.to_json())
    f = df.sum()
    Stats.objects(key=key).modify(upsert=True, **f)


def _build_stats_for_project_xform(survey_class, main_qs, fstats, pure_count,
                                   xform, key, rebuild):
    sync = SyncLog.objects(key=key).first() or _get_blank_sync_entry()
    
    # gets distinct dates for recently added records
    distinct_dates = survey_class.objects(_xform_id_string=xform.id_string,
                                          _id__gte=sync.start_id)\
                                 .distinct('datetime_today')
    
    if not rebuild and len(distinct_dates) == 0:
        return fstats 
    
    # pull records for distinct dates (new & old)
    fields = ('datetime_today','cin','rseq','acct_no','acct_status','meter_type')
    qs =  main_qs & Q(datetime_today__in=distinct_dates)
    records = survey_class.objects(qs).only(*fields)
    results = _summarize_for_stats_grouped_by(records, 'datetime_today')
    all_collected = False
    
    while results:
        for result in results:
            StatsBatch.objects(key=key, date=result.date)\
                      .modify(upsert=True, **result)
        
        alt_count = StatsBatch.objects(key=key).sum('count')
        if pure_count == alt_count:
            break
        else:
            StatsBatch.objects(key=key).delete()
        
        records = survey_class.objects(main_qs).only(*fields)
        results = _summarize_for_stats_grouped_by(records, 'datetime_today')
        all_collected = True
    
    if not all_collected:
        # need to do this so that the xform summary stats turns out accurate 
        records = survey_class.objects(main_qs).only(*fields)
        results = _summarize_for_stats_grouped_by(records, 'datetime_today')
    
    # save xform summary stats
    df = pd.DataFrame([dict(r) for r in results])
    df.drop('date', axis=1, inplace=True)
    f = df.sum()
    Stats.objects(key=key).modify(upsert=True, **f)


def _summarize_for_stats_grouped_by(records, groupby_key):
    df = pd.read_json(records.to_json())
    df.rename(columns={'datetime_today':'$dt'}, inplace=True)
    df['datetime_today'] = df['$dt'].apply(
        lambda r: datetime.fromtimestamp(r['$date']/1000).strftime('%Y-%m-%d'))
    
    grouped = df.groupby(groupby_key)
    tbl = grouped['cin'].count()
    
    results = []
    for i in range(len(tbl)):
        date_group = tbl.index[i]
        group = grouped.get_group(date_group)
        
        result = Storage(date=date_group, count=group.index.size)
        result.update(_summarize_batch(group))
        results.append(result)
    return results


def _summarize_batch(df):
    result = _summarize_duplicates(df)
    result.update(_summarize_by_acct_status(df))
    result.update(_summarize_by_meter_type(df))
    return result


def _summarize_duplicates(df):
    result, keys = Storage(), ('cin', 'rseq', 'acct_no')
    for key in keys:
        if key not in df.columns:
            df[key] = ''
        
        f = df[df[key].isnull() == False]
        f = f[f.duplicated(key) == True]
        result["dup_{}".format(key)] = f.index.size
    return result


def _summarize_by_acct_status(df):
    result, key = Storage(), 'acct_status'
    if not key in df.columns:
        df[key] = ''
    
    for value in VALUES_ACCT_STATUS:
        f = df[df[key] == value]
        result['acct_' + value.replace('-', '')] = f.index.size
    return result


def _summarize_by_meter_type(df):
    result, key = Storage(), 'meter_type'
    if not key in df.columns:
        df[key] = ''

    for value in VALUES_METER_TYPE:
        f = df[df[key] == value]
        result['meter_' + value] = f.index.size
    return result


def _get_blank_sync_entry():
    return Storage({
        'start_id': 0, 'count': 0,
        'synced_on': '', 'synced_by': '',
        'sync_pass': None, 'fail_info': None
    })


def _get_blank_stats_entry():
    return Storage({
        'count':0, 'dup_cin':0, 'dup_rseq':0, 'dup_acct_no':0,
        'acct_new':0, 'acct_existing':0, 'acct_nosupply':0, 
        'acct_ytbd':0, 'meter_ppm':0, 'meter_analogue':0,
        'meter_none':0
    })
