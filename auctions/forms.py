from django import forms

class EmailForm(forms.Form):
    recipient = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
