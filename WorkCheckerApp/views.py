from django.shortcuts import render, redirect, HttpResponse
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from .models import ErrorDoc
import os.path
import lxml
import zipfile
import re
from bs4 import BeautifulSoup

class DocError():
    number = 0
    errorType = ""
    errorDisc = ""
    chapter = ""
    text = ""

    def __init__(self, number, errorType, errorDisc, chapter, text):
        self.number = number
        self.errorType = errorType
        self.errorDisc = errorDisc
        self.chapter = chapter
        self.text = text

    def __str__(self):
        return '%s | %s | %s | %s | %s' % (self.number, self.errorType, self.errorDisc, self.chapter, self.text)

    def serialize(self):
        return self.__dict__

def parse(request, doc_path, html_path, doc_type, wct_path):
    errornum = 0
    if doc_type == 1:
        with open(wct_path, "r") as f:
            f.readline()
            request.session['FontSize'] = float(f.readline())
            request.session['FontName'] = f.readline()
            request.session['ParIndent'] = float(f.readline())
            request.session['TextAlign'] = f.readline()
            request.session['FLeft'] = float(f.readline())
            request.session['FRight'] = float(f.readline())
            request.session['FUp'] = float(f.readline())
            request.session['FDown'] = float(f.readline())
            request.session['LineSpace'] = float(f.readline())
            f.close()
    else:
        request.session['FontSize'] = 14
        request.session['FontName'] = 'Times New Roman'
        request.session['ParIndent'] = 36
        request.session['TextAlign'] = 'justify'
        request.session['FLeft'] = 10
        request.session['FRight'] = 10
        request.session['FUp'] = 10
        request.session['FDown'] = 10
        request.session['LineSpace'] = 12

    with open(html_path, "r") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'lxml')
        tags = soup.find_all()
        pars = soup.find_all("p")
        chapters = [[soup.new_tag("div")]]
        chapters[0][0].string = "[Начало документа]"
        currentChapter = 0

        for tag in tags:
            isHeader = False
            if tag.name in ["h1", "h2", "h3"] and re.search('\S', tag.text) != None:
                #print(tag.span.text)
                chapters.append([])
                currentChapter += 1
                chapters[currentChapter].append(tag)
                isHeader = True

            if tag.name == "p" and re.search('\S', tag.text) != None:
                bold = tag.b
                if bold != None and bold.span != None and re.search('\S', tag.span.text) != None:
                    parAtr = tag.attrs["style"]
                    parStyles = re.split(";|,", parAtr.replace('\n', ""))
                    for parStyle in parStyles:
                        if parStyle.find('text-align:') != -1:
                            ta = parStyle[parStyle.find(':') + 1:]
                            if ta == "center":
                                chapters.append([])
                                currentChapter += 1
                                chapters[currentChapter].append(tag)
                                isHeader = True
                if 'class' in tag.attrs and str(tag.attrs['class'][0]) in ["MsoNoSpacing", "MsoTocHeading"]:
                    print("gotcha")
                    chapters.append([])
                    currentChapter += 1
                    chapters[currentChapter].append(tag)
                    isHeader = True
                spanChild = None
                for child in tag.children:
                    if child.name == "span" and re.search('\S', child.text) != None:
                        spanChild = child
                        if "style" in spanChild.attrs:
                            spanAtr = spanChild.attrs["style"]
                            spanStyles = re.split(";|,", spanAtr.replace('\n', ""))
                            for spanStyle in spanStyles:
                                if spanStyle.find("font-family:") != -1:
                                    ff = spanStyle[spanStyle.find(':') + 1:]
                                    ff = ff.replace('\"', "")
                                    if ff != request.session['FontName'] and ff != "Symbol" and ff != "Wingdings":
                                        if errornum != 0:
                                            lastError = request.session['ErrorList'][errornum-1]
                                            if lastError['errorType'] != "Неподходящий шрифт" and  lastError['errorDisc'] != 'Должен быть шрифт "' + request.session['FontName'] + '". У вас стоит шрифт "' + ff + '".' and lastError['chapter'] != chapters[currentChapter][0].text and lastError['text'] != tag.text:
                                                errornum += 1
                                                request.session['ErrorList'].append(DocError(errornum, "Неподходящий шрифт", 'Должен быть шрифт "' + request.session['FontName'] + '". У вас стоит шрифт "' + ff + '".', chapters[currentChapter][0].text, tag.text).serialize())
                                        else:
                                            errornum += 1
                                            request.session['ErrorList'].append(DocError(errornum, "Неподходящий шрифт", 'Должен быть шрифт "' + request.session['FontName'] + '". У вас стоит шрифт "' + ff + '".', chapters[currentChapter][0].text, tag.text).serialize())
                                if spanStyle.find("font-size:") != -1:
                                    fs = spanStyle[spanStyle.find(':') + 1:]
                                    fs = fs[:fs.find('.')]
                                    if float(fs) != float(request.session['FontSize']):
                                        if errornum != 0:
                                            lastError = request.session['ErrorList'][errornum-1]
                                            if lastError['errorType'] != "Неподходящий размер шрифта" and  lastError['errorDisc'] != 'Размер шрифта должен быть равен "' + str(request.session['FontSize']) + '". У вас размер шрифта равен "' + str(fs) + '".' and lastError['chapter'] != chapters[currentChapter][0].text and lastError['text'] != tag.text:
                                                errornum += 1
                                                request.session['ErrorList'].append(DocError(errornum, "Неподходящий размер шрифта", 'Размер шрифта должен быть равен "' + str(request.session['FontSize']) + '". У вас размер шрифта равен "' + str(fs) + '".', chapters[currentChapter][0].text, tag.text).serialize())
                                        else:
                                            errornum += 1
                                            request.session['ErrorList'].append(DocError(errornum, "Неподходящий размер шрифта", 'Размер шрифта должен быть равен "' + str(request.session['FontSize']) + '". У вас размер шрифта равен "' + str(fs) + '".', chapters[currentChapter][0].text, tag.text).serialize())

                if "style" in tag.attrs and not isHeader:
                    parAtr = tag.attrs["style"]
                    parStyles = re.split(";|,", parAtr.replace('\n', ""))

                    hasParentTd = False
                    try:
                        if tag.parent.name == "td":
                            hasParentTd = True
                    except:
                        pass
                    
                    if not hasParentTd:
                        for parStyle in parStyles:
                            if parStyle.find('margin-top:') != -1:
                                mt = parStyle[parStyle.find(':') + 1:]
                                mt = mt[:mt.find('.')]
                                if float(mt) != request.session['LineSpace'] and float(mt) != 0:
                                    errornum += 1
                                    request.session['ErrorList'].append(DocError(errornum, "Неподходящий межстрочный интервал", 'Межстрочный интервал должен быть равен "' + str(request.session['LineSpace']) + '". У вас межстрочный интервал равен "' + str(mt) + '".', chapters[currentChapter][0].text, tag.text).serialize())
                                # print("mt:" + mt)

                            if parStyle.find('text-align:') != -1 and currentChapter > 0:
                                ta = parStyle[parStyle.find(':') + 1:]
                                if ta != request.session['TextAlign']:
                                    textAl = ""
                                    textAlTrue = ""
                                    if ta == "justify":
                                        textAl = "по ширине"
                                    elif ta == "center":
                                        textAl = "по центру"
                                    elif ta == "left":
                                        textAl = "по левой стороне"
                                    elif ta == "right":
                                        textAl = "по правой стороне"
                                    else:
                                        textAl = "неизвестным образом"
                                    if request.session['TextAlign'] == "justify":
                                        textAlTrue = "по ширине"
                                    elif request.session['TextAlign'] == "center":
                                        textAlTrue = "по центру"
                                    elif request.session['TextAlign'] == "left":
                                        textAlTrue = "по левой стороне"
                                    elif request.session['TextAlign'] == "right":
                                        textAlTrue = "по правой стороне"
                                    else:
                                        textAlTrue == "неизвестным образом"
                                    errornum += 1
                                    request.session['ErrorList'].append(DocError(errornum, "Неподходящее выравнивание текста", 'Выравнивание текста должно быть выставлено ' + textAlTrue + '. У вас оно выставлено ' + textAl + '.', chapters[currentChapter][0].text, tag.text).serialize())
                                # print("ta:" + ta)
                                
                            if parStyle.find('text-indent:') != -1:
                                ti = parStyle[parStyle.find(':') + 1:]
                                if ti.find('.') != -1:
                                    ti = ti[:ti.find('.')]
                                if ti.find('cm') != -1:
                                    ti = ti[:ti.find('cm')]
                                if float(ti) != request.session['ParIndent'] and float(ti) > 0:
                                    errornum += 1
                                    request.session['ErrorList'].append(DocError(errornum, "Неподходящий абзацный отступ", 'Абзацный отступ должен быть равен "' + str(request.session['ParIndent']) + '". У вас абзацный отступ равен "' + str(ti) + '".', chapters[currentChapter][0].text, tag.text).serialize())
                                # print("ti:" + ti)
        #print(len(chapters))
        for ch in chapters:
            print(ch[0].text)
            print("---------------------------------------------------------------------------")
            pass
    #print(doc_path + '\n' + html_path + '\n' + doc_type + '\n' + wct_path)

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
            #print(os.path.exists(os.getcwd() + '\\media\\' + request.session['DocName']))
        else:
            notDoc = True
        if 'HtmlFile' in request.FILES:
            myfile = request.FILES['HtmlFile']
            fs = FileSystemStorage()
            request.session['HtmlName'] = fs.save(myfile.name, myfile)
            #print(os.path.exists(os.getcwd() + '\\media\\' + request.session['HtmlName']))
        else:
            notHtml = True
        if 'DocType' in request.POST:
            request.session['DocType'] = request.POST['DocType']
            #print(request.session['DocType'])
        if 'CustomTemplate' in request.FILES:
            myfile = request.FILES['CustomTemplate']
            fs = FileSystemStorage()
            request.session['CustomTemplate'] = fs.save(os.getcwd()+'\\media\\templates\\' + myfile.name, myfile)
            #print(os.path.exists(request.session['CustomTemplate']))
        else:
            if request.session['DocType'] == "2":
                notWCT = True
        
        if notDoc or notHtml or notWCT:
            return render(request, 'checker.html', {'notDoc': notDoc, 'notHtml': notHtml, 'notWCT': notWCT})

        #------------PARSING-------------

        arrayErr = []
        request.session['ErrorList'] = arrayErr

        parse(request, os.getcwd() + '\\media\\' + request.session['DocName'], os.getcwd() + '\\media\\' + request.session['HtmlName'], request.session['DocType'], request.session['CustomTemplate'])

        #request.session['ErrorList'].append(DocError(1, "Error1", "Error1Description", "").serialize())
        #request.session['ErrorList'].append(DocError(2, "Error2", "Error2Description", "").serialize())
        #request.session['ErrorList'].append(DocError(3, "Error3", "Error3Description", "").serialize())

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
            return response
        #if os.path.exists(os.getcwd()+'\\WCT\\'+request.session['TemplateName']+'.wct'):
            #os.remove(os.getcwd()+'\\WCT\\'+request.session['TemplateName']+'.wct')

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