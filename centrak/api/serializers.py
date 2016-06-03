from rest_framework_mongoengine.serializers import DocumentSerializer
from enumeration.models import XForm



class XFormSerializer(DocumentSerializer):
    
    class Meta:
        model = XForm
