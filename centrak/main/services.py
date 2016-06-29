from enumeration import signals, tasks


def handle_post_survey_import(sender, **kwargs):
    results = kwargs.get('results', None)
    if not results:
        return
    
    # raise the merge tasks for processed update forms
    uform_long_ids = [fid for fid in results.keys() if '_cu' in fid]
    if not uform_long_ids:
        return
    tasks.merge_survey_updates.delay(uform_long_ids, merged_by='auto')
    print('called-:-post_survey_import_handler')
 

def handle_post_survey_merge(sender, **kwargs):
    print('got some merge results')
    print(kwargs.get('results', None))


signals.post_survey_import.connect(handle_post_survey_import)
signals.post_survey_merge.connect(handle_post_survey_merge)
