from django.contrib.auth.decorators import user_passes_test
from django.conf import settings



INVALID_SERVICE_KEY_CHAR = r" `~!@#$%^&*({[</\>]})+=,:;?'"


##:: ==+ decorators
def admin_with_permission(perm=None, login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user 'is_staff' and has particular
    permission enabled, redirecting to the log-in page if necessary. If the 
    raise_exception parameter is given the PermissionDenied exception is raised.
    """
    def check_perms(user):
        # ensure that user is a staff to access the ADMIN AREA
        if not user.is_staff:
            return False
        if not perm:
            return True
        
        # extracted from django.contrib.auth.decorators.permission_required
        if not isinstance(perm, (list, tuple)):
            perms = (perm,)
        else:
            perms = perm
        
        # first check if the user has the permission (even anonymous users)
        if user.has_perms(perms):
            return True
        # in clase 403 handler should be called raise the Exception
        if raise_exception:
            raise PermissionDenied
        # as last resort, show login form
        return False
    return user_passes_test(check_perms, login_url=login_url)


def has_object_permission(user, obj, add_perm, change_perm, pk='id'):
    """
    Determines whether user has permission to create or change an object based
    on the status (new, existing) of the object. 
    """
    assert add_perm not in ('', None) or change_perm not in ('', None)
    if not getattr(obj, pk):
        if add_perm and user.has_perm(add_perm):
            return (True, None)
    else:
        if change_perm and user.has_perm(change_perm):
            return (True, None)
    return (False, redirect(reverse('login')))


##:: ==+ general utility funcs
def has_valid_email_domain(email):
    """
    Determines whether provided email belongs to the official domain configured
    at settings.CENTRAK_OFFICIAL_DOMAINS
    """
    if email:
        domain = email.split('@')[1]
        return domain.lower() in settings.CENTRAK_OFFICIAL_DOMAINS
    return False


def is_valid_official_email_format(email, fname, lname):
    """
    Determines whether provided email is in desired official format.
    """
    strip = lambda x: x.replace("'", '').replace('-', '').lower()
    if email and fname and lname:
        name_parts = [n for n in (email.split('@')[0]).split('.') if n]
        if len(name_parts) == 2:
            for name in name_parts:
                if name == strip(fname) or name == strip(lname):
                    return True
    return False


def is_valid_service_key(key):
    if not key or [c for c in key if c in INVALID_SERVICE_KEY_CHAR]:
        return False
    return True