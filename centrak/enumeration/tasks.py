from datetime import datetime
from celery.decorators import task
from django.core.cache import cache

from enumeration.models import Project
from enumeration.services import import_surveys, merge_updates



@task(name="tasks.scheduled-survey-import")
def scheduled_survey_import():
    """Discovers all active projects marked for auto-sync and syncs all 
    associated XForms.
    """
    target_projects = (Project.objects(active=True, auto_sync=True, 
                                       status__ne=Project.STATUS_CONCLUDED)
                              .only('code','xforms','uforms'))
    
    for p in target_projects:
        xform_long_ids = (p.xforms or [])[:] + (p.uforms or [])[:]
        import_surveys(xform_long_ids, synced_by='auto')
        
        # invalidate caches for the project and forms
        cache_key = "project.{}".format(p.code)
        cache.delete(cache_key)
        
        for xform_long_id in xform_long_ids:
            cache.delete("{}.form.{}".format(cache_key, xform_long_id))


@task(name="tasks.merge-updates")
def merge_survey_updates(uform_long_ids, merged_by):
    merge_updates(
        uform_long_ids, 
        merged_by
    )

