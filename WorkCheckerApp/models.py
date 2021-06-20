from django.db import models
from .validator import *

class Document(models.Model):
    TEMPLATE_TYPES = (
    ("1", "Отчет по курсовой работе"),
    ("2", "Отчет по производственной практике"),
    ("3", "Отчет по дипломной работе"),
    ("4", "Свой шаблон проверки")
    )

    document = models.FileField(upload_to='documents/', validators=[doc_validator])
    templateType = models.CharField(max_length=1, choices=TEMPLATE_TYPES, default = '1')
    template = models.FileField(upload_to='templates/', validators=[wct_validator], blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return '%s | %s | %s' % (self.document, self.templateType, self.template)

class ErrorDoc(models.Model):
    number = models.CharField(max_length=10)
    errorType = models.CharField(max_length=100)
    errorDisc = models.CharField(max_length=1000)
    pageNum = models.CharField(max_length=10)
    lineNum = models.CharField(max_length=10)
    solution = models.CharField(max_length=100)
    
    def __str__(self):
        return '%s | %s' % (self.number, self.errorType)