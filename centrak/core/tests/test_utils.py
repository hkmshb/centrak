import pytest
from core.utils import Storage



class TestStorage(object):

    def test_storage_is_instance_of_dict(self):
        s = Storage()
        assert isinstance(s, dict) == True

    def test_can_access_element_using_dot_notation(self):
        foo = Storage()
        foo['bar'] = 'baz-qux-norf'
        assert foo.bar == 'baz-qux-norf'

    def test_can_set_element_using_dot_notation(self):
        foo = Storage()
        foo.bar = 'baz-qux-norf'
        assert foo['bar'] == 'baz-qux-norf'

    def test_access_using_unknown_member_returns_None(self):
        foo = Storage()
        assert foo.bar == None

    def test_access_using_missing_key_returns_None(self):
        foo = Storage()
        assert foo['bar'] == None

    def test_can_be_pickled_and_unpickled(self):
        import pickle

        foo = Storage(bar='baz')
        out = pickle.dumps(foo)
        assert out != None
        
        qux = pickle.loads(out)
        assert qux.bar == 'baz'

    def test_has_friendly_string_representation(self):
        foo = Storage(bar='baz')
        assert repr(foo).startswith('<Storage') == True
    
    def test_make_not_given_dict_or_sequence_throws(self):
        with pytest.raises(ValueError):
            Storage.make('foo')

    def test_can_make_storage_from_dict(self):
        obj = Storage.make(dict(foo='bar'))
        assert isinstance(obj, Storage) == True
        assert obj.foo == 'bar'

    def test_can_make_storage_from_nested_dicts(self):
        obj = Storage.make(dict(
            baz = dict(
                quux = 'norf',
                meta = dict(
                    name = 'simple.conf',
                    path = r'c:\path\to\conf',
                )
            )
        ))
        assert isinstance(obj, Storage) == True
        assert isinstance(obj.baz, Storage) == True
        assert isinstance(obj.baz.meta, Storage) == True
