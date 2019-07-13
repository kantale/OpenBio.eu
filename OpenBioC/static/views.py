from django.shortcuts import render

from .forms import ContactForm

def static_en(request):
    '''
    Static site english version
    '''

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        print ('Is valid?', contact_form.is_valid())
        print ('name:')
        print (contact_form.cleaned_data['name'])
    else:
        contact_form = ContactForm()

    context = {
        'contact_form': contact_form,
    }

    return render(request, 'static/index_static_en.html', context)

def static_gr(request):
    '''
    English site english version
    '''

    context = {}

    return render(request, 'static/index_static_gr.html', context)

