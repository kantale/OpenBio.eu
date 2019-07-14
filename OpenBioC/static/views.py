from django.shortcuts import render
from django.core.mail import send_mail


from .forms import ContactForm

def static_en(request):
    '''
    Static site english version
    '''

    error_message = ''
    success_message = ''
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            name = contact_form.cleaned_data['name']
            subject = contact_form.cleaned_data['subject']
            message = contact_form.cleaned_data['message']
            sender = contact_form.cleaned_data['sender']

            send_message = '''
MAIL FROM CONTACT FORM OF: https://www.openbio.eu 

NAME: {name}

FROM: {sender}

SUBJECT: {subject}


MESSAGE:
=====
{message}
=====
END OF MESSAGE
'''.format(message=message, subject=subject, sender=sender, name=name)
            send_subject = 'MAIL FROM CONTACT FORM OF: https://www.openbio.eu'

            try:
                send_mail(send_subject, send_message, 'info@openbio.eu', ['alexandros.kanterakis@gmail.com'])
            except Exception as e:
                error_message = 'Could not send message.'
            else:
                success_message = 'Your message was sent.'
        else:
            error_message = 'Could not send message. Please update invalid fields.'

    else:
        contact_form = ContactForm()

    context = {
        'error_message': error_message,
        'contact_form': contact_form,
    }

    return render(request, 'static/index_static_en.html', context)

def static_gr(request):
    '''
    English site english version
    '''

    context = {}

    return render(request, 'static/index_static_gr.html', context)

