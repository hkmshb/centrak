from django.dispatch import Signal


post_survey_import = Signal(providing_args=["results"])
post_survey_merge  = Signal(providing_args=["results"])
