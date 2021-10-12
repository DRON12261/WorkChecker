from django.db import models

class ErrorDoc(models.Model):
    number = models.CharField(max_length=10)
    errorType = models.CharField(max_length=100)
    errorDisc = models.CharField(max_length=1000)
    pageNum = models.CharField(max_length=10)
    lineNum = models.CharField(max_length=10)
    solution = models.CharField(max_length=100)
    
    def __str__(self):
        return '%s | %s' % (self.number, self.errorType)