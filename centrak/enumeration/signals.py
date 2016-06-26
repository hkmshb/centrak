from django.dispatch import Signal


post_survey_import = Signal(providing_args=["results"])
