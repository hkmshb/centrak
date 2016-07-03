import copy
import logging
from datetime import datetime
from requests.exceptions import ConnectionError

from django.conf import settings
from mongoengine.queryset import Q

from core.utils import get_survey_auth_token, ApiClient, Storage
from .models import SyncLog, XForm, Survey, Capture, Update
from . import signals



def import_surveys(xform_long_ids, synced_by=None):
    auth_token = get_survey_auth_token()
    api_client = ApiClient(settings.SURVEY_API_ROOT, auth_token)
    importer = SurveyImporter(api_client)
    
    results, last_synced = ({}, datetime.now())
    for xform_long_id in xform_long_ids:
        result = importer.execute(xform_long_id)
        results[xform_long_id] = result
        
        if not result.errors:
            # update xform sync details
            try:
                XForm.objects(id_string=xform_long_id).update_one(
                    last_synced = last_synced,
                    synced_by = synced_by)
            except Exception as ex:
                msg = "XForm update after sync failed. Error: %s"
                logging.error(msg, str(ex), exc_info=True)
            
            # log sync operation
            if result.count > 0:
                try:
                    form_key = "project.{}.form.{}".format(
                        xform_long_id[:4], xform_long_id)
                    
                    SyncLog.objects.create(key=form_key, 
                        count=result.count,
                        start_id=result.start_id,
                        synced_by=synced_by,
                        synced_on=last_synced,
                        sync_pass=result.errors in (None, []),
                        fail_info=(result.errors or [])[:])
                except Exception as ex2:
                    msg = "Sync stats update failed. Error: %s"
                    logging.error(msg, str(ex2), exc_info=True)
    
    signals.post_survey_import.send(sender=None, results=results)
    return results


def merge_updates(uform_long_ids, merged_by=None):
    merger = SurveyMerger()
    
    results = {}
    for uform_long_id in uform_long_ids:
        result = merger.execute(uform_long_id, merged_by)
        results[uform_long_id] = result
        
    signals.post_survey_merge.send(sender=None, results=results)
    return results


class SurveyTransformer(object):

    #: default transform rules
    RULE_NAMES = ('exclude','name_change_map','text_transform_map')
    DEFAULT_RULES = {
        'exclude': [
            '_bamboo_dataset_id',
            'meta/instanceID',
            'formhub/uuid',
            '_geolocation',
            '_submitted_by',
            '_duration',
            '_status',
        ],
        'name_change_map': {
            'multi_source': 'multi',
            'occupant_status': 'occupant',
            'addr_gps': 'gps',
        },
        'text_transform_map': {
            'upper': [
                'cin_station',
                'enum_id'
            ]
        }
    }

    def __init__(self, rules=None):
        self.__rules = rules or SurveyTransformer.DEFAULT_RULES
    
    def get_rules(self):
        return self.__rules
    
    def merge_into_rules(self, rules):
        if rules in (None, {}):
            return
        
        current_rules = self.get_rules()
        for rule_name in SurveyTransformer.RULE_NAMES:
            rule_targets = rules.get(rule_name, None)
            if not rule_targets:
                continue
            
            # insert blank rule_targets into current_rules for missing
            # rule_names as appropriate for rule in question...
            targets_ = current_rules.get(rule_name, None)
            if not targets_:
                blank_targets = {} if rule_name.endswith('_map') else []
                current_rules[rule_name] = blank_targets 
            
            for target in rule_targets:
                marked_for_removal = target.startswith('-:')
                target_exists = target[2:] in current_rules[rule_name]
                if marked_for_removal and target_exists:
                    if not rule_name.endswith('_map'):
                        current_rules[rule_name].remove(target[2:])
                    else:
                        del current_rules[rule_name][target[2:]]
                elif not marked_for_removal:
                    if not rule_name.endswith('_map'):
                        if not target_exists:
                            current_rules[rule_name].append(target)
                    else:
                        current_rules[rule_name].update({
                            target: rules[rule_name][target] 
                        })
        self.__rules = current_rules
    
    def replace_rules(self, rules):
        rules = rules or {}
        self.__rules = rules
    
    def transform(self, survey):
        survey_ = copy.deepcopy(survey)
        out = self._do_transform(survey_)
        out = self._do_post_transform(out, survey_)
        return out
    
    def _do_transform(self, survey):
        """This operation applies defined rules to transform a survey entry.
        
        Part of the operation include key cleanup, where section_labels are
        removed before and rules are then applied.
        """
        all_rules = self.get_rules()
        rules_excl = all_rules.get('exclude', [])
        rules_ncmap = all_rules.get('name_change_map', {})
        rules_ttmap = all_rules.get('text_transform_map', {})

        text_transform_ops = {
            'upper': lambda x: x.upper(),
            'lower': lambda x: x.lower(),
            'title': lambda x: x.title()
        }

        output = {}
        for key, value in survey.items():
            # rule: exclude
            if key in rules_excl:
                continue

            # flatten keys having section labels i.e key that are in the
            # form: "section_label/key_name"
            if '/' in key:
                section_label, ikey = key.split('/')
                # rule: exclude
                if ikey in rules_excl:
                    continue
                else:
                    # assign inner key to the outside key
                    key = ikey
            
            # rule: name_map
            if key in rules_ncmap:
                key = rules_ncmap[key]
            output[key] = value

            # rule: text transform
            for op_key in text_transform_ops.keys():
                if key in rules_ttmap.get(op_key, {}):
                    op = text_transform_ops[op_key]
                    output[key] = op(output[key])
        return output
    
    def _do_post_transform(self, transform_output, survey):
        # hint: snapshots should go into a separate table
        transform_output['gps'] = (
            [] if 'gps' not in transform_output else
                [float(v) for v in transform_output['gps'].split(' ')])
        
        pjt_id_parts = transform_output['_xform_id_string'].split('_')
        project_id = "{}".format(pjt_id_parts[0])
        transform_output['project_id'] = project_id

        transform_output['group'] = transform_output['enum_id'][0]
        transform_output['station'] = transform_output['cin_station']
        transform_output['upriser'] = "{}/{}".format(
                transform_output['cin_station'],
                transform_output['cin_ltroute'][0])
        transform_output['cin'] = "{}/{}/{}".format(
                transform_output['cin_station'],
                transform_output['cin_ltroute'],
                transform_output['cin_custno'])
        transform_output['date_created'] = datetime.today().isoformat()
        transform_output['last_updated'] = None
        transform_output['dropped'] = False
        transform_output['rseq'] = "{}/{}".format(
                transform_output['upriser'],
                transform_output['cin_custno'])
                
        key = 'neighbour_cin'
        if key in transform_output and transform_output[key] != None:
            transform_output['neighbour_rseq'] = "{}/{}".format(
                    transform_output['upriser'],
                    transform_output[key])
        return transform_output


class SurveyImporter(object):
    
    def __init__(self, api_client):
        self.api_client = api_client
        self._exec_result = None
    
    def __call__(self, xform_long_id):
        self.execute(xform_long_id)
    
    def _add_error(self, message):
        self._exec_result.errors.append(message)
    
    def execute(self, xform_long_id):
        # startup exec result need to be set here
        self._exec_result = Storage(errors=[], count=0, 
            xform_long_id=xform_long_id, start_id=-1)
        
        # retrieve form
        xform = XForm.objects.get(id_string=xform_long_id)
        if not xform:
            msg = "XForm with specified id '{}' not found."
            self._add_error(msg.format(xform_long_id))
            return self._exec_result
        
        # get total item count which would be used as the starting ref
        # for the record pull from the API rest service
        model = Capture if xform.type == XForm.TYPE_CAPTURE else Update
        record_count = model.objects(_xform_id_string=xform.id_string).count()
        
        transformer_class = SurveyTransformer
        
        # pull new surveys
        try:
            transformed, transformer = ([], transformer_class())
            survey_class = Capture if xform.type == XForm.TYPE_CAPTURE else Update
            for surveys in self.api_client.get_survey(xform.object_id, start=record_count):
                logging.debug("surveys pulled: %s", len(surveys))
                if surveys:
                    self._exec_result.count += len(surveys)
                    for survey in surveys:
                        t = transformer.transform(survey)
                        transformed.append(survey_class(**t))
                        
                        if self._exec_result.start_id == -1:
                            self._exec_result.start_id = t['_id']
                    
                    model.objects.insert(transformed)
                    transformed = []
        except ConnectionError:
            self._add_error("Sync failed. Ensure your Internet connection is active.")
        except Exception as ex:
            self._add_error("Sync failed. %s" % str(ex))
            logging.error("Sync failed. %s", str(ex), exc_info=True)
        return self._exec_result


class SurveyMerger(object):
    
    DEFAULT_FIELDS = Survey._fields_ordered
    DEFAULT_RULES = {
        'exclude_re': [
            '_*', 
            'datetime_*'
        ],
        'exclude': [ 
            'project_id', 
            'date_created',
            'last_updated',
            'dropped',
            'merged',
            'merged_by'
        ],
        'match': ['cin', 'rseq'],
        'list_fields': ['gps', 'remarks']
    }
    
    def __init__(self):
        self._exec_result = None
    
    def __call__(self, uform_long_id, merged_by=None):
        self.execute(uform_long_id, merged_by)
    
    def _add_error(self, message):
        if self._exec_result == None:
            self._exec_result = self._make_result_storage()
        self._exec_result.errors.append(message)
    
    def _do_merge(self, capture, update, merged_by):
        rules_all  = SurveyMerger.DEFAULT_RULES
        rules_excl_re = rules_all['exclude_re']
        rules_excl    = rules_all['exclude']
        rules_match   = rules_all['match']
        rules_lfield  = rules_all['list_fields']
        
        # get/make snapshot
        snapshot = Capture(**capture.to_dict())
        if capture.snapshots in (None, {}):
            capture.snapshots = {'origin': {'capture': snapshot}}
        
        for field in rules_match:
            if capture[field] != update[field]:
                msg = "Update with cin '{}' cannot be merged into capture with cin '{}'."
                self._add_error(msg.format(update.cin, capture.cin))
                return
        
        for field in SurveyMerger.DEFAULT_FIELDS:
            if field in rules_excl or self._matches_any(rules_excl_re, field):
                continue
            
            if field in rules_lfield and field == 'gps':
                if update[field] in (None, []):
                    continue
                
                if capture[field][-1] < update[field][-1]:
                    continue
                
            capture[field] = update[field]
            self._save_update(snapshot, capture, update, merged_by)
    
    def _matches_any(self, re_rules, field):
        for r in re_rules:
            if r.endswith('*') and field.startswith(r.replace('*','')):
                return True
            elif r.startswith('*') and field.endswith(r.replace('*','')):
                return True
        return False
    
    def _make_result_storage(self):
        return Storage(
            errors=[], merged_cins=[],
            count=0, xform_long_id=None
        )
    
    def _save_update(self, capture_snapshot, capture, update, merged_by):
        try:
            last_updated = datetime.now()
            capture['last_updated'] = last_updated
            capture['updated_by'] = {'username': merged_by}
            capture.save()
            
            update['merged'] = True
            update['dropped'] = True
            update['updated_by'] = {'username': merged_by}
            update.save()
            
            self._exec_result.merged_cins.append(capture.cin)
        except Exception as ex:
            # rollback captures
            capture_snapshot.save()
            
            update['merged'] = False
            update['dropped'] = False
            update['updated_by'] = {}
            update.save()
            raise
    
    def execute(self, uform_long_id, merged_by=None):
        # startup exec result need to be set here
        self._exec_result = self._make_result_storage()
        self._exec_result.xform_long_id = uform_long_id
        
        # retrieve form
        xform = XForm.objects.get(id_string=uform_long_id)
        if not xform:
            msg = "XForm with specified id '{}' not found."
            self._add_error(msg.format(uform_long_id))
            return self._exec_result
        
        if xform.type != XForm.TYPE_UPDATE:
            self._add_error("Invalid form id provided. Expected id for an "
                            "Update type XForm.")
            return self._exec_result
        
        # get updates that haven't been dropped and merged
        try:
            updates = Update.objects(Q(_xform_id_string=xform.id_string) &
                                     (Q(dropped=False) | Q(merged=False)))
            for update in updates:
                capture = Capture.objects(cin=update.cin, rseq=update.rseq).first()
                if capture == None:
                    continue
                self._do_merge(capture, update, merged_by)
        except ConnectionError:
            self._add_error("sync failed. Ensure your Internet connection is active.")
        except Exception as ex:
            self._add_error("Sync failed. %s" % str(ex))
            logging.error("Sync failed. %s", str(ex), exc_info=True)
        return self._exec_result

