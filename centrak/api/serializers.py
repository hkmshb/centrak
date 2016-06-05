from rest_framework import serializers
from rest_framework_mongoengine import serializers as mserializers
from enumeration.models import PowerStation, PowerLine, XForm



#:+--------------------------------------------------------------------------+
#: NETWORK MODEL SERIALIZERS
#:+--------------------------------------------------------------------------+

class PowerStationSerializer(mserializers.DocumentSerializer):
    
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = PowerStation
    
    def get_fullname(self, obj):
        return str(obj)


class PowerLineSerializer(mserializers.DocumentSerializer):
    class Meta:
        model = PowerLine


#:+--------------------------------------------------------------------------+
#: ENUM. RESX. SERIALIZERS
#:+--------------------------------------------------------------------------+

class XFormSerializer(mserializers.DocumentSerializer):
    
    class Meta:
        model = XForm
