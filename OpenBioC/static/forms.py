from django import forms

class ContactForm_en(forms.Form):

	name = forms.CharField(max_length=100, widget=forms.TextInput(
		attrs={
			'class': 'form-control',
			'placeholder': 'Full Name',
		}))
	subject = forms.CharField(max_length=100, widget=forms.TextInput(
		attrs={
			'class': 'form-control',
			'placeholder': 'Subject',
		}))
	message = forms.CharField(widget=forms.Textarea(
		attrs={
			'class': 'form-control',
			'placeholder': 'Message',
		}))
	sender = forms.EmailField(widget=forms.EmailInput(
		attrs={
			'class': 'form-control',
			'placeholder': 'Your Email',
		}))


class ContactForm_gr(forms.Form):

	name = forms.CharField(max_length=100, widget=forms.TextInput(
		attrs={
			'class': 'form-control',
			'placeholder': 'Όνομα',
		}))
	subject = forms.CharField(max_length=100, widget=forms.TextInput(
		attrs={
			'class': 'form-control',
			'placeholder': 'Θέμα',
		}))
	message = forms.CharField(widget=forms.Textarea(
		attrs={
			'class': 'form-control',
			'placeholder': 'Μήνυμα',
		}))
	sender = forms.EmailField(widget=forms.EmailInput(
		attrs={
			'class': 'form-control',
			'placeholder': 'Διεύθυνση email',
		}))

