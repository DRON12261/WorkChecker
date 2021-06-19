from django.shortcuts import render, redirect
from .forms import DocumentForm

def main(request):
    return redirect('checker')

def checker(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('sas.html')
    else:
        form = DocumentForm()

    context = {
        'form': form
    }
    
    return render(request, 'checker.html', context)

def constructor(request):
    return render(request, 'constructor.html')

def sas(request):
    return render(request, 'sas.html')