import pytest
from core import utils



class TestUserEmail(object):

    @pytest.mark.parametrize("email", [
        "john.doe@gmail.com", "john.doe@yahoo.com",
        "john.doe@hotmail.com", "john.doe@kedco.com.ng",
        "john@zoho.com", "john.doe@aol.com", "john.doe@mail.com",
        "john@yandex.com", "john@outlook.com", "john@inbox.com",
        "john@gmx.com", "john@mailinator.com", "john@icloud.com"])
    def test_fails_for_email_with_non_official_domain(self, email):
        assert utils.has_valid_email_domain(email) == False
    
    @pytest.mark.parametrize("email", [    
        "john@kedco.ng", "john@kedco.net", "john.doe@tmp.kedco.ng"])
    def test_true_for_email_with_official_domain(self, email):
        assert utils.has_valid_email_domain(email) == True
    
    @pytest.mark.parametrize("fname,lname,email", [
        # format.. name.name
        ('john', 'doe', 'john@kedco.ng'),
        ('john', 'doe', 'johndoe@kedco.ng'),
        # format.. either name appearing
        ('john', 'doe', 'johnson.mark@kedco.ng'),
        ('john', 'doe', 'd.johnsom@tmp.kedco.ng')])
    def test_fails_for_first_or_lastname_not_appearing_in_email(self, fname, lname, email):
        assert utils.is_valid_official_email_format(email, fname, lname) == False
    
    @pytest.mark.parametrize("fname,lname,email", [
        ('john', 'doe', 'john.doe@kedco.ng'),
        ('john', 'doe', 'jane.doe@kedco.ng'),
        ('john', 'doe', 'doe.johnson@kedco.ng'),
        # names with special characters..
        ("ja'afar", "musa", 'm.jaafar@kedco.net'),
        ('abdul-lahi', 'usman', 'abdullahi.usman@kedco.ng')])
    def test_passes_for_first_or_lastname_in_valid_domained_email(self, fname, lname, email):
        assert utils.is_valid_official_email_format(email, fname, lname) == True


class TestUtilityFunctions(object):

    @pytest.mark.parametrize("key", [
        "sample key", "sample'key", "sample/key", "sample\\key", "sample~key", 
        "sample@key", "sample#key", "sample$key", "sample%key", "sample^key", 
        "sample&key", "sample*key", "sample(key", "sample)key", "sample+key", 
        "sample=key", "sample,key", "sample?key"])
    def test_cleanup_fails_for_key_with_defined_invalid_chars(self, key):
        assert utils.INVALID_SERVICE_KEY_CHAR != None
        assert utils.is_valid_service_key(key) == False
