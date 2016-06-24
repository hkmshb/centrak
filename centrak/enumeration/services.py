import copy
import logging
import requests
from datetime import datetime

from django.conf import settings

from core.utils import get_survey_auth_token, ApiClient, Storage
from .models import SyncLog, XForm, Capture, Update
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
        project_id = "{}_{}".format(pjt_id_parts[0], pjt_id_parts[-1])
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


class CentrackbSurveyTransformer(SurveyTransformer):
    EXTRA_RULES = {
        'name_change_map': {
            'kangis_no': 'kg_Id',
            'landlord_name': 'new_tholder',
            'addr_no': 'addy_no',
            'addr_street': 'addy_street',
            'addr_state': 'addy_state',
            'addr_lga': 'addy_lga',
            'tariff_pp': 'tariff_new',
        }
    }

    def __init__(self):
        super(CentrackbSurveyTransformer, self).__init__()
        self.merge_into_rules(CentrackbSurveyTransformer.EXTRA_RULES)
    
    def _do_post_transform(self, transform_output, survey):
        output = super(CentrackbSurveyTransformer, self)._do_post_transform(
                    transform_output, survey)
        
        output['snapshots'] = {}
        output['rseq'] = "{}/{}".format(
            output['upriser'], output['cin_custno'])
        
        key = 'neighbour_cin'
        if key in output and output[key]:
            output['neighbour_rseq'] = "{}/{}".format(
                output['upriser'], output[key])
        return output


class SurveyImporter(object):
    
    def __init__(self, api_client, centrackb_compatible=False):
        self.centrackb_compatible = centrackb_compatible
        self.api_client = api_client
        self._exec_result = None
    
    def __call__(self):
        self.execute()
    
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
            return False
        
        # get total item count which would be used as the starting ref
        # for the record pull from the API rest service
        model = Capture if xform.type == XForm.TYPE_CAPTURE else Update
        record_count = model.objects(_xform_id_string=xform.id_string).count()
        
        transformer_class = SurveyTransformer
        if self.centrackb_compatible:
            transformer_class = CentrackbSurveyTransformer
        
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

