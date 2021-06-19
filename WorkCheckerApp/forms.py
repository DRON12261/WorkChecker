from django import forms
from .models import Document
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document', )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('document', css_class='form-control form-control-lg')
        )