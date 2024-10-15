from rest_framework.serializers import ModelSerializer
from .models import EntryPass

class EntryPassSerializer(ModelSerializer):
    class Meta:
        model = EntryPass
        fields = '__all__'