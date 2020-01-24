from app.models import Tool, Workflow


from rest_framework import status
from rest_framework import viewsets
#from app.serializers import ToolSerializer

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.core.exceptions import ObjectDoesNotExist

#class ToolViewSet(viewsets.ReadOnlyModelViewSet):
#    """
#    API endpoint for Tools
#    """
#    #queryset = Tool.objects.all().order_by('-created_at')
#    queryset = Tool.objects.filter(name__in=['samtools', 'hapmap3', 'bioconvert']).order_by('-created_at')
#    serializer_class = ToolSerializer


#=====================
#===TOOLS=============
#=====================

class ToolSerializer(serializers.Serializer):
	name = serializers.CharField(max_length=200)
	version = serializers.CharField(max_length=200)
	edit = serializers.IntegerField()


@api_view(['GET'])
def tool_name(request, tool_name):
	if request.method == 'GET':
		tools = Tool.objects.filter(name=tool_name)
		serializer = ToolSerializer(tools, many=True)
		return Response(serializer.data)
	else:
		return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def tool_name_version(request, tool_name, tool_version):
	if request.method == 'GET':
		tools = Tool.objects.filter(name=tool_name, version=tool_version)
		serializer = ToolSerializer(tools, many=True)
		return Response(serializer.data)
	else:
		return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def tool_complete(request, tool_name, tool_version, tool_edit):
	if request.method == 'GET':
		try:
			tool = Tool.objects.get(name=tool_name, version=tool_version, edit=int(tool_edit))
		except ObjectDoesNotExist as e:
			return Response(status=status.HTTP_404_NOT_FOUND)
		serializer = ToolSerializer(tool, many=False)
		return Response(serializer.data)
	else:
		return Response(status=status.HTTP_404_NOT_FOUND)

#==============================
#=========WORKFLOWS============
#==============================

class WorkflowSerializer(serializers.Serializer):
	name = serializers.CharField(max_length=200)
	edit = serializers.IntegerField()

class WorkflowSerializerDAG(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'test_1': instance.name,
            'test_2': instance.edit + 7
        }

@api_view(['GET'])
def workflow_name(request, workflow_name):
	if request.method == 'GET':
		workflows = Workflow.objects.filter(name=workflow_name)
		serializer = WorkflowSerializer(workflows, many=True)
		return Response(serializer.data)
	else:
		return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def workflow_complete(request, workflow_name, workflow_edit):
	if request.method == 'GET':

		dag = request.query_params.get('dag')
		dag = dag == 'true'

		try:
			workflow = Workflow.objects.get(name=workflow_name, edit=int(workflow_edit))
		except ObjectDoesNotExist as e:
			return Response(status=status.HTTP_404_NOT_FOUND)
		if dag:
			serializer = WorkflowSerializerDAG(workflow, many=False)
		else:
			serializer = WorkflowSerializer(workflow, many=False)
			
		return Response(serializer.data)
	else:
		return Response(status=status.HTTP_404_NOT_FOUND)




