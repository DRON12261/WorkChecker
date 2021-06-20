from django.contrib import admin
from .models import Document, ErrorDoc

admin.site.register(Document)
admin.site.register(ErrorDoc)