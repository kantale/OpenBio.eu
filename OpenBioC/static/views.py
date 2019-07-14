from django.shortcuts import render
from django.core.mail import send_mail


from .forms import ContactForm_en, ContactForm_gr

def create_context(request, language):
    '''
    Create the context of static site
    '''

    assert language in ['en', 'gr']

    if language == 'en':
        ContactForm = ContactForm_en
    elif language == 'gr':
        ContactForm = ContactForm_gr

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
                if language == 'en':
                    error_message = 'Could not send message. Please send mail to: kantale@ics.forth.gr'
                elif language == 'gr':
                    error_message = 'Εμφανίστηκε σφάλμα. Το μήνυμα δεν στάλθηκε. Μπορείτε να επικοινωνήσετε στο kantale@ics.forth.gr'
            else:
                if language == 'en':
                    success_message = 'Your message was sent.'
                elif language == 'gr':
                    success_message = 'Το μήνυμα στάλθηκε.'
        else:
            if language == 'en':
                error_message = 'Could not send message. Please update invalid fields.'
            elif language == 'gr':
                error_message = 'Το μήνυμα δεν στάληθκε. Κάποια πεδία δεν είναι σωστά συμπληρωμένα.'
    else:
        contact_form = ContactForm()

    context = {
        'error_message': error_message,
        'contact_form': contact_form,
    }

    return context


def static_en(request):
    '''
    Static site english version
    '''

    context = create_context(request, 'en')
    return render(request, 'static/index_static_en.html', context)

def static_gr(request):
    '''
    English site english version
    '''

    context = create_context(request, 'gr')

    return render(request, 'static/index_static_gr.html', context)

