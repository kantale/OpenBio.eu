from app.models import Tool

from rest_framework import viewsets
from app.serializers import ToolSerializer


class ToolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Tools
    """
    #queryset = Tool.objects.all().order_by('-created_at')
    queryset = Tool.objects.filter(name__in=['samtools', 'hapmap3', 'bioconvert']).order_by('-created_at')
    serializer_class = ToolSerializer

