from app.models import Tool, Workflow


from rest_framework import status
from rest_framework import viewsets
#from app.serializers import ToolSerializer

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import BaseRenderer, JSONRenderer, BrowsableAPIRenderer

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

#class WorkflowSerializer(serializers.Serializer):
#    name = serializers.CharField(max_length=200)
#    edit = serializers.IntegerField()

class BinaryRenderer_TARGZ(BaseRenderer):
    media_type = 'application/gzip'
    format = 'binary'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class BinaryRenderer_ZIP(BaseRenderer):
    media_type = 'application/zip'
    format = 'binary'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class CustomBrowsableAPIRenderer(BrowsableAPIRenderer):
    def get_default_renderer(self, view):
        return JSONRenderer()

def return_binary(format_):
    return format_ in ['CWLTARGZ', 'CWLZIP']

class WorkflowSerializerDAG(serializers.BaseSerializer):
    '''
    Returns a Workflow for execution in various formats
    '''

    def set_request(self, request):
        self.request = request

    def set_workflow_id(self, workflow_id):
        self.workflow_id = workflow_id

    def set_workflow_format(self, format_):
        self.format_ = format_.upper()

    def to_representation(self, instance):
        '''
        Call run_workflow to get a dag representation of the workflow
        '''

        # Should we return a binary object?
        ret_binary = return_binary(self.format_)

        if ret_binary:
            # Return binary object
            do_url_quote = False
            return_bytes = True
        elif self.format_ == 'JSON':
            do_url_quote = False
            return_bytes = False
        else:
            do_url_quote = True
            return_bytes = False

        # instance is the workflow object
        args = {
            'workflow': {'name': instance.name, 'edit': instance.edit},
            'workflow_info_editable': False, # This workflow is saved 
            'download_type': self.format_,
            'workflow_id': self.workflow_id,
            'obc_client': True, # Declare that we need an airflow DAG explicitly for the OBC client
            'workflow_options': {}, # Workflow options . An interesting idea is to get them from the REST API
            'do_url_quote': do_url_quote, # In case of binary Do not url encode objects . We need the bytes object
            'return_bytes': return_bytes, # Return bytes ?
        }

        returned_object = download_workflow(self.request, **args)
        if ret_binary:
            return returned_object

        deserialized_content =  simplejson.loads(returned_object.content)
        if not 'output_object' in deserialized_content:
            return {
                'success': False,
                'error': deserialized_content['error_message'],
            }

        # If necessary, unquote content
        if do_url_quote:
            output_object = urllib.parse.unquote(deserialized_content['output_object'])
        else:
            output_object = deserialized_content['output_object']

        if self.format_ == 'JSON':
            output_object = simplejson.loads(output_object)

        return {
            'success': True,
            'name': instance.name,
            'edit': instance.edit,
            'format': self.format_,
            'workflow': output_object, # returned_object['output_object'], # Do we need to return all output_object info?
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
@renderer_classes([BinaryRenderer_TARGZ, BinaryRenderer_ZIP, JSONRenderer, CustomBrowsableAPIRenderer]) #  , JSONRenderer, CustomBrowsableAPIRenderer, BrowsableAPIRenderer
def workflow_complete(request, workflow_name, workflow_edit):
    '''
    Called from urls.py 
    '''

    if request.method == 'GET':

        # i.e. /?format=airflow
        format_ = request.query_params.get('format')
        format_ = str(format_).upper()
        if not format_ in ['JSON', 'BASH', 'CWLTARGZ', 'CWLZIP', 'AIRFLOW']:
            return Response({'success': False, 'error': 'Unsupported or Undefined format',}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


        # /?workflow_id=xyz
        workflow_id = request.query_params.get('workflow_id')

        try:
            workflow = Workflow.objects.get(name=workflow_name, edit=int(workflow_edit))
        except ObjectDoesNotExist as e:
            return Response({'success': False, 'error': 'Workflow not found'}, status=status.HTTP_404_NOT_FOUND)

        
        serializer = WorkflowSerializerDAG(workflow, many=False)
        serializer.set_request(request)
        serializer.set_workflow_id(workflow_id)
        serializer.set_workflow_format(format_)

        filename = None
        if format_ == 'CWLTARGZ':
            filename = 'workflow.tar.gz'
        elif format_ == 'CWLZIP':
            filename = 'workflow.zip'

        if filename:
            return Response(serializer.data, headers={'Content-Disposition': 'attachment; filename={}'.format(filename)})
        else:
            return Response(serializer.data)

    else:
        return Response(status=status.HTTP_404_NOT_FOUND)




