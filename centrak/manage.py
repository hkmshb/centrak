#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "centrak.settings")

    from django.core.management import execute_from_command_line
    
    # imports below help to listen and handle superuser creation
    import django; django.setup()
    from main import signals    


    execute_from_command_line(sys.argv)
