from app.models import Tool

from rest_framework import serializers

class ToolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tool
        fields = ['name', 'version', 'edit']

