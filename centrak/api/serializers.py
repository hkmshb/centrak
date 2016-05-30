from rest_framework import serializers
from enumeration.models import XForm


class XFormSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = XForm
        fields = ('id', 'object_id', 'id_string', 'title', 'type',
                  'description', 'is_active', 'api_url', 'synced_by',
                  'last_synced', 'date_imported')