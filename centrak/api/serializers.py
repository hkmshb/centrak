from rest_framework_mongoengine.serializers import DocumentSerializer
from enumeration.models import PowerStation, PowerLine, XForm



#:+--------------------------------------------------------------------------+
#: NETWORK MODEL SERIALIZERS
#:+--------------------------------------------------------------------------+

class PowerStationSerializer(DocumentSerializer):
    class Meta:
        model = PowerStation


class PowerLineSerializer(DocumentSerializer):
    class Meta:
        model = PowerLine


#:+--------------------------------------------------------------------------+
#: ENUM. RESX. SERIALIZERS
#:+--------------------------------------------------------------------------+

class XFormSerializer(DocumentSerializer):
    
    class Meta:
        model = XForm
