from django.shortcuts import render, redirect, HttpResponse
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from .models import ErrorDoc
import os.path

class DocError():
    number = 0
    errorType = ""
    errorDisc = ""
    pageNum = 0
    lineNum = 0
    solution = ""

    def __init__(self, number, errorType, errorDisc, pageNum, lineNum, solution):
        self.number = number
        self.errorType = errorType
        self.errorDisc = errorDisc
        self.pageNum = pageNum
        self.lineNum = lineNum
        self.solution = solution

    def __str__(self):
        return '%s | %s | %s | %s | %s | %s' % (self.number, self.errorType, self.errorDisc, self.pageNum, self.lineNum, self.solution)

    def serialize(self):
        return self.__dict__

def parse(doc_path, doc_type, wct_path):
    print(doc_path + '\n' + doc_type + '\n' + wct_path)

def checker(request):
    if 'DocName' not in request.session:
        request.session['DocName'] = ""
    if 'HtmlName' not in request.session:
        request.session['HtmlName'] = ""
    if 'DocType' not in request.session:
        request.session['DocType'] = 0
    if 'CustomTemplate' not in request.session:
        request.session['CustomTemplate'] = ""
    if 'ErrorList' not in request.session:
        arrayErr = []
        request.session['ErrorList'] = arrayErr

    if request.method == "POST":
        notDoc = False
        notHtml = False
        notWCT = False
        if 'DocFile' in request.FILES:
            myfile = request.FILES['DocFile']
            fs = FileSystemStorage()
            request.session['DocName'] = fs.save(myfile.name, myfile)
            print(os.path.exists(os.getcwd() + '\\media\\' + request.session['DocName']))
        else:
            notDoc = True
        if 'HtmlFile' in request.FILES:
            myfile = request.FILES['HtmlFile']
            fs = FileSystemStorage()
            request.session['HtmlName'] = fs.save(myfile.name, myfile)
            print(os.path.exists(os.getcwd() + '\\media\\' + request.session['HtmlName']))
        else:
            notHtml = True
        if 'DocType' in request.POST:
            request.session['DocType'] = request.POST['DocType']
            print(request.session['DocType'])
        if 'CustomTemplate' in request.FILES:
            myfile = request.FILES['CustomTemplate']
            fs = FileSystemStorage()
            request.session['CustomTemplate'] = fs.save(os.getcwd()+'\\media\\templates\\' + myfile.name, myfile)
            print(os.path.exists(request.session['CustomTemplate']))
        else:
            if request.session['DocType'] == "2":
                notWCT = True
        
        if notDoc or notHtml or notWCT:
            return render(request, 'checker.html', {'notDoc': notDoc, 'notHtml': notHtml, 'notWCT': notWCT})

        #------------PARSING-------------

        arrayErr = []
        request.session['ErrorList'] = arrayErr

        parse(os.getcwd() + '\\media\\' + request.session['DocName'], request.session['DocType'], request.session['CustomTemplate'])

        request.session['ErrorList'].append(DocError(1, "Error1", "Error1Description", 3, 24, "").serialize())
        request.session['ErrorList'].append(DocError(2, "Error2", "Error2Description", 5, 223, "").serialize())
        request.session['ErrorList'].append(DocError(3, "Error3", "Error3Description", 14, 1, "").serialize())

        #--------------------------------

        if os.path.exists(os.getcwd()+'\\media\\' + request.session['DocName']):
            os.remove(os.getcwd()+'\\media\\' + request.session['DocName'])
        if os.path.exists(request.session['CustomTemplate']):
            os.remove(request.session['CustomTemplate'])
        
        return redirect('errors')

    return render(request, 'checker.html')

def constructor(request):
    if 'TemplateName' not in request.session:
        request.session['TemplateName'] = 'Новый шаблон'
    if 'FontSize' not in request.session:
        request.session['FontSize'] = 12
    if 'FontName' not in request.session:
        request.session['FontName'] = 'Times New Roman'
    if 'ParIndent' not in request.session:
        request.session['ParIndent'] = 10
    if 'TextAlign' not in request.session:
        request.session['TextAlign'] = 10
    if 'FLeft' not in request.session:
        request.session['FLeft'] = 10
    if 'FRight' not in request.session:
        request.session['FRight'] = 10
    if 'FUp' not in request.session:
        request.session['FUp'] = 10
    if 'FDown' not in request.session:
        request.session['FDown'] = 10
    if 'LineSpace' not in request.session:
        request.session['LineSpace'] = 10
    if 'Struct1' not in request.session:
        request.session['Struct1'] = True
    if 'Struct2' not in request.session:
        request.session['Struct2'] = True
    if 'Struct3' not in request.session:
        request.session['Struct3'] = True
    '''if 'Struct4' not in request.session:
        request.session['Struct4'] = True'''
    if 'Struct5' not in request.session:
        request.session['Struct5'] = True
    if 'Struct6' not in request.session:
        request.session['Struct6'] = True
    if 'Struct7' not in request.session:
        request.session['Struct7'] = False
    if 'Struct8' not in request.session:
        request.session['Struct8'] = False
    if 'Struct9' not in request.session:
        request.session['Struct9'] = False
    if 'Struct10' not in request.session:
        request.session['Struct10'] = False
    '''if 'Lit1' not in request.session:
        request.session['Lit1'] = True
    if 'Lit2' not in request.session:
        request.session['Lit2'] = True
    if 'Lit3' not in request.session:
        request.session['Lit3'] = True
    if 'Lit4' not in request.session:
        request.session['Lit4'] = True
    if 'Lit5' not in request.session:
        request.session['Lit5'] = False
    if 'Lit6' not in request.session:
        request.session['Lit6'] = False
    if 'Lit7' not in request.session:
        request.session['Lit7'] = False
    if 'ALit1' not in request.session:
        request.session['ALit1'] = False
    if 'ALit2' not in request.session:
        request.session['ALit2'] = True
    if 'ALit3' not in request.session:
        request.session['ALit3'] = False
    if 'ALit4' not in request.session:
        request.session['ALit4'] = True
    if 'ALit5' not in request.session:
        request.session['ALit5'] = False'''

    if request.method == 'POST':
        request.session['TemplateName'] = request.POST['TemplateName']
        request.session['FontSize'] = request.POST['FontSize']
        request.session['FontName'] = request.POST['FontName']
        request.session['ParIndent'] = request.POST['ParIndent']
        request.session['TextAlign'] = request.POST['TextAlign']
        request.session['FLeft'] = request.POST['FLeft']
        request.session['FRight'] = request.POST['FRight']
        request.session['FUp'] = request.POST['FUp']
        request.session['FDown'] = request.POST['FDown']
        request.session['LineSpace'] = request.POST['LineSpace']
        if 'Struct1' in request.POST:
            request.session['Struct1'] = True
        else:
            request.session['Struct1'] = False
        if 'Struct2' in request.POST:
            request.session['Struct2'] = True
        else:
            request.session['Struct2'] = False
        if 'Struct3' in request.POST:
            request.session['Struct3'] = True
        else:
            request.session['Struct3'] = False
        '''if 'Struct4' in request.POST:
            request.session['Struct4'] = True
        else:
            request.session['Struct4'] = False'''
        if 'Struct5' in request.POST:
            request.session['Struct5'] = True
        else:
            request.session['Struct5'] = False
        if 'Struct6' in request.POST:
            request.session['Struct6'] = True
        else:
            request.session['Struct6'] = False
        if 'Struct7' in request.POST:
            request.session['Struct7'] = True
        else:
            request.session['Struct7'] = False
        if 'Struct8' in request.POST:
            request.session['Struct8'] = True
        else:
            request.session['Struct8'] = False
        if 'Struct9' in request.POST:
            request.session['Struct9'] = True
        else:
            request.session['Struct9'] = False
        if 'Struct10' in request.POST:
            request.session['Struct10'] = True
        else:
            request.session['Struct10'] = False
        '''if 'Lit1' in request.POST:
            request.session['Lit1'] = True
        else:
            request.session['Lit1'] = False
        if 'Lit2' in request.POST:
            request.session['Lit2'] = True
        else:
            request.session['Lit2'] = False
        if 'Lit3' in request.POST:
            request.session['Lit3'] = True
        else:
            request.session['Lit3'] = False
        if 'Lit4' in request.POST:
            request.session['Lit4'] = True
        else:
            request.session['Lit4'] = False
        if 'Lit5' in request.POST:
            request.session['Lit5'] = True
        else:
            request.session['Lit5'] = False
        if 'Lit6' in request.POST:
            request.session['Lit6'] = True
        else:
            request.session['Lit6'] = False
        if 'Lit7' in request.POST:
            request.session['Lit7'] = True
        else:
            request.session['Lit7'] = False
        if 'ALit1' in request.POST:
            request.session['ALit1'] = True
        else:
            request.session['ALit1'] = False
        if 'ALit2' in request.POST:
            request.session['ALit2'] = True
        else:
            request.session['ALit2'] = False
        if 'ALit3' in request.POST:
            request.session['ALit3'] = True
        else:
            request.session['ALit3'] = False
        if 'ALit4' in request.POST:
            request.session['ALit4'] = True
        else:
            request.session['ALit4'] = False
        if 'ALit5' in request.POST:
            request.session['ALit5'] = True
        else:
            request.session['ALit5'] = False'''

        WCTFile = open(os.getcwd()+'\\WCT\\'+request.session['TemplateName']+'.wct', 'w')
        WCTFile.write(request.session['TemplateName']+'\n')
        WCTFile.write(request.session['FontSize']+'\n')
        WCTFile.write(request.session['FontName']+'\n')
        WCTFile.write(request.session['ParIndent']+'\n')
        WCTFile.write(request.session['TextAlign']+'\n')
        WCTFile.write(request.session['FLeft']+'\n')
        WCTFile.write(request.session['FRight']+'\n')
        WCTFile.write(request.session['FUp']+'\n')
        WCTFile.write(request.session['FDown']+'\n')
        WCTFile.write(request.session['LineSpace']+'\n')
        WCTFile.write(str(int(request.session['Struct1']))+str(int(request.session['Struct2']))+str(int(request.session['Struct3']))+str(int(request.session['Struct5']))+str(int(request.session['Struct6']))+str(int(request.session['Struct7']))+str(int(request.session['Struct8']))+str(int(request.session['Struct9']))+str(int(request.session['Struct10']))+'\n')
        '''WCTFile.write(str(int(request.session['Lit1']))+str(int(request.session['Lit2']))+str(int(request.session['Lit3']))+str(int(request.session['Lit4']))+str(int(request.session['Lit5']))+str(int(request.session['Lit6']))+str(int(request.session['Lit7']))+'\n')
        WCTFile.write(str(int(request.session['ALit1']))+str(int(request.session['ALit2']))+str(int(request.session['ALit3']))+str(int(request.session['ALit4']))+str(int(request.session['ALit5'])))'''
        WCTFile.close()

        with open(os.getcwd()+'\\WCT\\'+request.session['TemplateName']+'.wct', 'rb') as fh:
            response = FileResponse(open(os.getcwd()+'\\WCT\\'+request.session['TemplateName']+'.wct', 'rb'))
            if os.path.exist(os.getcwd()+'\\WCT\\'+request.session['TemplateName']+'.wct'):
                os.remove(os.getcwd()+'\\WCT\\'+request.session['TemplateName']+'.wct')
            return response

    return render(request, 'constructor.html')

def errors(request):
    if 'ErrorList' not in request.session:
        request.session['ErrorList'] = []

    context = {
        "ErrorList": request.session['ErrorList']
    }

    return render(request, 'errors.html', context)

def main(request):
    return redirect('checker')