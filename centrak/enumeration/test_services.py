import pytest
from datetime import datetime, timedelta
from .models import Capture, Update
from .services import SurveyTransformer, SurveyMerger



class SurveyRuleTransformer(SurveyTransformer):
    """Focuses on rule application and by-passes post transform logic."""
    
    def _do_post_transform(self, transform_output, survey):
        return transform_output


class SurveyRuleMerger(SurveyMerger):
    """Focuses on rule application and by-passes collection update."""
    
    def __init__(self, test_callback):
        super(SurveyRuleMerger, self).__init__()
        self.test_callback = test_callback
    
    def _save_update(self, capture_snapshot, capture, update, merged_by):
        """Overriden to capture and pass onto test callback the resulting
           survey object (capture) after the merge operation.
        """
        self.test_callback(self, capture)


class TestSurveyTransform(object):

    def _get_transformer(self):
        return SurveyRuleTransformer({
            'exclude': ['key1','key2'],
            'name_change_map': {'key-a':'key-a2', 'key-b':'key-b2'}
        })

    def test_transformer_has_default_rules(self):
        transformer = SurveyRuleTransformer()
        assert transformer.get_rules() not in (None, {})

    def test_can_replace_transformr_rules(self):
        transformer = SurveyRuleTransformer()
        transformer.replace_rules({})
        assert transformer.get_rules() == {}
    
    def test_rules_marked_for_removal_absent_from_resulting_merge(self):
        transformer = self._get_transformer()
        transformer.merge_into_rules({
            'exclude':['-:key2'], 'name_change_map': {'-:key-a':None}})
        
        latest_rules = transformer.get_rules()
        assert len(latest_rules['exclude']) == 1
        assert 'key1' in latest_rules['exclude']
        assert 'key2' not in latest_rules['exclude']

        assert len(latest_rules['name_change_map']) == 1
        assert 'key-b' in latest_rules['name_change_map']
        assert 'key-a' not in latest_rules['name_change_map']
    
    def test_new_rules_present_in_resulting_merge(self):
        transformer = self._get_transformer()
        transformer.merge_into_rules({
            'exclude': ['key3'], 'name_change_map': {'key-c':'key-charlie'}})
        
        latest_rules = transformer.get_rules()
        assert len(latest_rules['exclude']) == 3
        assert len(latest_rules['name_change_map']) == 3
    
    def test_transform_cleans_up_keys_with_section_label(self):
        transformer = self._get_transformer()
        capture = {
            'section_label/key-x':'value-x',
            'dumb-label/key-y': 'value-y'}
        
        output = transformer.transform(capture)
        assert output not in (None, {})
        assert len(capture) == 2
        assert 'key-x' in output
        assert 'key-y' in output
    
    def test_transform_applies_exclude_rules(self):
        transformer = self._get_transformer()
        capture = {'key1': 'value-1', 'key-x': 'value-x'}
        output = transformer.transform(capture)
        assert len(output) == 1
        assert 'key1' not in output
    
    def test_transform_applies_name_change_map_rules(self):
        transformer = self._get_transformer()
        capture = {'key-a':'value-a', 'key-x':'value-x'}
        output = transformer.transform(capture)
        assert len(output) == 2
        assert 'key-a2' in output and output['key-a2'] == 'value-a'
    
    def test_transform_applies_text_transform_map_rules(self):
        transformer = self._get_transformer()
        transformer.merge_into_rules({
            'text_transform_map': {'upper': ['key-a2']}
        })
        capture = {'key-a':'value-a'}
        output = transformer.transform(capture)
        assert len(output) == 1
        assert output['key-a2'] == 'VALUE-A' 


class TestSurveyMerger(object):
    
    def _get_surveys(self):
        return (
            Capture(_id=10, _version='15', _xform_id_string='f30b_cf_KN',
                group='B', station='S30123', upriser='S30123/1',
                cin='S30123/1/01/01/0001', rseq='S30123/1/0001', 
                datetime_today=datetime.now(), device_imei='c:device-imei', 
                project_id='c:pjt-id', last_updated=datetime.today()),
                
            Update(_id=20, _version='25', _xform_id_string='f30b_cu_KN',
                group='D', station='S30123', upriser='S30123/1',
                cin='S30123/1/01/01/0001', rseq='S30123/1/0001',
                datetime_today=datetime.now() + timedelta(3),
                device_imei='u:device-imei', project_id='u:pjt-id',
                acct_status='existing', acct_no='33/20/01/0098-01',
                tariff='R1', plot_type='residential')
        )
    
    def _do_test(self, test_func, capture, update):
        merger = SurveyRuleMerger(test_func)
        merger._do_merge(capture, update, None)
    
    def test_exclude_rules(self):
        capture, update = self._get_surveys()
        def t_(merger, merged_capture):
            assert merged_capture._id == 10
            assert merged_capture._xform_id_string == 'f30b_cf_KN'
            assert merged_capture.project_id == 'c:pjt-id'
            assert merged_capture.datetime_today.strftime('%Y-%m-%d')\
                        == datetime.now().strftime('%Y-%m-%d')
            assert merger._exec_result == None
            
        self._do_test(t_, capture, update)
    
    def test_match_rules_as_merge_fails_for_non_matching_fields(self):
        merger = SurveyRuleMerger(lambda x, y: None)
        capture, update = self._get_surveys()
        update.cin += 'X'
        
        merger._do_merge(capture, update, None)
        assert len(merger._exec_result.errors) == 1
    
    def test_merged_attributes(self):
        capture, update = self._get_surveys()
        def t_(merger, merged_capture):
            pass
        
        self._do_test(t_, capture, update)

