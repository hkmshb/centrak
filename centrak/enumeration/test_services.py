import pytest
from .services import SurveyTransformer



class SurveyRuleTransformer(SurveyTransformer):
    """Focuses on rule application and bypasses post transform logic."""

    def _do_post_transform(self, transform_output, survey):
        return transform_output



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
