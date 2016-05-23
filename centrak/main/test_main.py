import pytest
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from .forms import UserRegistrationForm

User = get_user_model()



class RegistrationViewTestCase(TestCase):
    
    _url_register = reverse('register')
    _url_registration_complete = reverse('registration-complete')
    
    def test_uses_form_template_for_registration(self):
        response = self.client.get(self._url_register)
        self.assertTemplateUsed(response, 'account/registration_form.html')
    
    def test_uses_notice_template_for_completed_registration(self):
        response = self.client.get(self._url_registration_complete)
        self.assertTemplateUsed(response, 'account/registration_complete.html')

@pytest.mark.django_db
class TestUserRegistrationForm(object):
    
    _form_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@kedco.ng',
        'password1': 'secret',
        'password2': 'secret'
    }
   
    @pytest.mark.parametrize("omitted_field", ['first_name', 'last_name']) 
    def test_validation_fails_for_omitted_field(self, omitted_field):
        form_data = self._form_data.copy()
        del form_data[omitted_field]
        
        form = UserRegistrationForm(data=form_data)
        assert form.is_valid() == False
    
    def test_validation_fails_for_omitted_email(self):
        form_data = self._form_data.copy()
        del form_data['email']
        
        form = UserRegistrationForm(data=form_data)
        assert form.is_valid() == False
    
    def test_validation_fails_for_password1_and_password2_mismatch(self):
        form_data = self._form_data.copy()
        form_data['password2'] = 'not-a-secret'
        form = UserRegistrationForm(data=form_data)
        assert form.is_valid() == False
    
    def test_email_used_as_username_for_created_user(self):
        form = UserRegistrationForm(data=self._form_data)
        assert form.is_valid() == True
        
        user = form.save()
        assert (
            user and user.id and 
            user.username == user.email and
            user.username == self._form_data['email']
        )
    
    def test_registered_user_is_inactive_by_default(self):
        form = UserRegistrationForm(data=self._form_data)
        user = form.save()
        assert user and user.id and user.is_active == False
    
    def test_validation_fails_for_email_already_in_use(self):
        user = User.objects.create_user(
                    username='john.doe@kedco.ng', 
                    email='john.doe@kedco.ng',
                    password='@pwd') 
        
        form = UserRegistrationForm(data=self._form_data)
        assert form.is_valid() == False
    
    @pytest.mark.parametrize("email_domain,expected", [
        ('kedco.ng', True), ('kedco.net', True), ('kedco.com', False), 
        ('tmp.kedco.ng', True), ('tmp.kedco.net', False), ('2.kedco.ng', False), 
        ('survey.kedco.ng', False), ('centrak.kedco.ng', False), ('gmail.com', False),
        ('yahoo.com', False), ('hotmail.com', False), ('mailinator.com', False),
    ])
    def test_permitted_email_domains(self, email_domain, expected):
        tmp_email = 'john.doe@{}'.format(email_domain)
        assert UserRegistrationForm.has_valid_email_domain(tmp_email) == expected
    
    @pytest.mark.parametrize("email_part,fname,lname,expected", [
        ('john.doe', 'john', 'doe', True), ('john.doe', 'doe', 'john', True),
        ('john.doe', 'john', 'max', True), ('john.doe', 'jane', 'max', False),
        ('john_doe', 'john', 'doe', False),('john', 'john', 'doe', False)
    ])
    def test_permitted_email_formats(self, email_part, fname, lname, expected):
        tmp_mail = '{}@kedco.ng'.format(email_part)
        func = UserRegistrationForm.is_valid_kedco_email_format
        assert func(tmp_mail, fname, lname) == expected
    