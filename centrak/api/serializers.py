from rest_framework import serializers

from core.models import ApiServiceInfo



class ApiServiceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiServiceInfo

