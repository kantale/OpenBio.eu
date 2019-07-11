from django.shortcuts import render

# Create your views here.

def static_en(request):
    '''
    Static site english version
    '''

    context = {}

    return render(request, 'static/index_static_en.html', context)

def static_gr(request):
    '''
    English site english version
    '''

    context = {}

    return render(request, 'static/index_static_gr.html', context)

