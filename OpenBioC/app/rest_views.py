from app.models import Tool, Workflow


from rest_framework import status
from rest_framework import viewsets
#from app.serializers import ToolSerializer

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.core.exceptions import ObjectDoesNotExist

from .views import download_workflow # Import from main views

import simplejson
import urllib.parse

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

    def set_request(self, request):
        self.request = request

    def set_workflow_id(self, workflow_id):
        self.workflow_id = workflow_id

    def to_representation(self, instance):
        '''
        Call run_workflow to get a dag representation of the workflow
        '''

        # instance is the workflow object
        args = {
            'workflow': {'name': instance.name, 'edit': instance.edit},
            'workflow_info_editable': False, # This workflow is saved 
            'download_type': 'AIRFLOW',
            'workflow_id': self.workflow_id,
            'workflow_options': {}, # Workflow options . An interesting idea is to get them from the REST API
        }

        returned_object = download_workflow(self.request, **args)
        deserialized_content =  simplejson.loads(returned_object.content)
        if not 'output_object' in deserialized_content:
            return {
                'success': False,
                'error': deserialized_content['error_message'],
            }

        output_object = urllib.parse.unquote(deserialized_content['output_object'])

        return {
            'success': True,
            'name': instance.name,
            'edit': instance.edit,
            'dag': output_object, # returned_object['output_object'], # Do we need to return all output_object info?
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
    '''
    Called from urls.py 
    '''

    if request.method == 'GET':

        # /?dag=true
        dag = request.query_params.get('dag')
        dag = dag == 'true'

        # /?workflow_id=xyz
        workflow_id = request.query_params.get('workflow_id')


        try:
            workflow = Workflow.objects.get(name=workflow_name, edit=int(workflow_edit))
        except ObjectDoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if dag:
            serializer = WorkflowSerializerDAG(workflow, many=False)
            serializer.set_request(request)
            serializer.set_workflow_id(workflow_id)
        else:
            serializer = WorkflowSerializer(workflow, many=False)

        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)




