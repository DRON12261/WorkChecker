from django.shortcuts import render, redirect
from .forms import DocumentForm
from .models import Document, ErrorDoc

class DocErr():
    number = ""
    errorType = ""
    errorDisc = ""
    pageNum = ""
    lineNum = ""
    solution = ""
    rowType = ""
    
    def __init__ (self, number, errorType, errorDisc, pageNum, lineNum, solution, rowType):
        self.number = number
        self.errorType = errorType
        self.errorDisc = errorDisc
        self.pageNum = pageNum
        self.lineNum = lineNum
        self.solution = solution
        self.rowType = rowType
    
    def __str__(self):
        return 'LOL %s' % (self.number)

err1 = DocErr('1', 'Хуйня', 'Хуита какаято', '1', '23', 'Переделывай', 'danger')
err2 = DocErr('2', 'Хуйня', 'Хуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаято', '3', '2', 'Переделывай', 'danger')
err3 = DocErr('3', 'Хуйня', 'Хуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаятоХуита какаято', '3', '2', 'Переделывай', 'warning')

docErrors = [err1, err2, err3]

def main(request):
    return redirect('checker')

def checker(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            return render(request, 'errors.html')
    else:
        form = DocumentForm()

    context = {
        'form': form
    }
    
    return render(request, 'checker.html', context)

def constructor(request):
    return render(request, 'constructor.html')

def errors(request):
    context = {
        'docErrors': docErrors
    }
    
    return render(request, 'errors.html', context)