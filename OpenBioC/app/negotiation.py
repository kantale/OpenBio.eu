'''
Also declared in settings.py
See: https://www.django-rest-framework.org/api-guide/content-negotiation/ 
'''

from rest_framework.negotiation import BaseContentNegotiation

class IgnoreClientContentNegotiation(BaseContentNegotiation):

    def select_renderer(self, request, renderers, format_suffix):
        """
        Select the first renderer in the `.renderer_classes` list.
        """

        
        format_ = str(request.query_params.get('format')).upper()

        if format_ in ['CWLTARGZ', ]:
            return (renderers[0], renderers[0].media_type)
        elif format_ in ['CWLZIP', ]:
            return (renderers[1], renderers[1].media_type)
        else:
            return (renderers[2], renderers[2].media_type)

