from django.conf import settings



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
    if email and fname and lname:
        name_parts = [n for n in (email.split('@')[0]).split('.') if n]
        if len(name_parts) == 2:
            for name in name_parts:
                if name == fname.lower() or name == lname.lower():
                    return True
    return False
