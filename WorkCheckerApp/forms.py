from django import forms
from .models import Document
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document', 'templateType', 'template',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            HTML('<h1>Проверка работы</h1></br>'),
            Div(   
                HTML('<h4 for="formFileLg">Загрузить работу (.doc, .docx)</h4>'),
                Field('document', css_class='form-control form-control-lg'),
                css_class='border border-2 border-secondary rounded-3 p-3'
            ),
            HTML('</br>'),
            Div(
                HTML('<h4 for="formFileLg">Выберите шаблон проверки</h4>'),
                Field('templateType', css_class='form-select form-select-lg', id='templateType'),
                Div(
                    HTML('</br>'),
                    Div(
                        HTML('<h4 for="formFileLg">Загрузить свой шаблон (.wct)</h4>'),
                        Field('template', css_class='form-control form-control-lg'),
                        css_class='border border-1 border-info rounded-3 p-3'
                    ),
                    id='customTemplate'
                ),
                css_class='border border-2 border-secondary rounded-3 p-3'
            ),
            Div(
                Submit('submit', 'Запустить проверку', css_class='btn btn-dark btn-lg'),
                css_class='d-grid gap-2 mt-4 mb-4'
            )
        )