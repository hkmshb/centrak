from rest_framework_mongoengine import serializers as mserializers
from rest_framework import serializers

from core.models import ApiServiceInfo
from enumeration.models import XForm



class ApiServiceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiServiceInfo


class XFormSerializer(mserializers.DocumentSerializer):
    class Meta:
        model = XForm
