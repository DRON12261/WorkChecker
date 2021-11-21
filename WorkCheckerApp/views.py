from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
import os.path
import xml.dom.minidom
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
    chaptersStr = []
    chaptersHave = []
    if doc_type == "2":
        with open(wct_path, "r") as f:
            request.session['TemplateName'] = f.readline().replace('\n', "")
            request.session['FontSize'] = float(f.readline())
            request.session['FontName'] = f.readline().replace('\n', "")
            request.session['TextAlign'] = f.readline().replace('\n', "")
            request.session['FLeft'] = float(f.readline())
            request.session['FRight'] = float(f.readline())
            request.session['FUp'] = float(f.readline())
            request.session['FDown'] = float(f.readline())
            request.session['Structs'] = f.readline()
            f.close()
    else:
        request.session['TemplateName'] = "Отчет по курсовой работе"
        request.session['FontSize'] = 14
        request.session['FontName'] = 'Times New Roman'
        request.session['TextAlign'] = 'justify'
        request.session['FLeft'] = 3
        request.session['FRight'] = 1
        request.session['FUp'] = 2
        request.session['FDown'] = 2
        request.session['Structs'] = '11110000'

    for i in range(0, 8):
        if str(request.session['Structs'])[i] == '1':
            if i == 0:
                chaptersStr.append('Содержание')
            elif i == 1:
                chaptersStr.append('Введение')
            elif i == 2:
                chaptersStr.append('Заключение')
            elif i == 3:
                chaptersStr.append('Список литературы')
            elif i == 4:
                chaptersStr.append('Словарь сокращений')
            elif i == 5:
                chaptersStr.append('Словарь терминов')
            elif i == 6:
                chaptersStr.append('Список иллюстрированного материала')
            elif i == 7:
                chaptersStr.append('Приложения')

    z = zipfile.ZipFile(doc_path, 'r')
    z.extract('word/document.xml', 'TempDoc/')
    dom = xml.dom.minidom.parse('TempDoc/word/document.xml')
    dom.normalize()
    par = dom.getElementsByTagName("w:pgMar")[0]
    print("name = " + par.nodeName)
    for (name, value) in par.attributes.items():
        twipsInSM = 567.0
        print(name + " = " + value)
        if name == "w:top" and round(float(value)/twipsInSM, 1) != request.session['FUp']:
            errornum += 1
            request.session['ErrorList'].append(DocError(errornum, "Неподходящий размер верхнего поля страницы", 'Верхнее поле должно равняться ' + str(request.session['FUp']) + ' см. У вас верхнее поле равняется ' + str(round(float(value)/twipsInSM, 1)) + ' см.', '', '').serialize())
        if name == "w:bottom" and round(float(value)/twipsInSM, 1) != request.session['FDown']:
            errornum += 1
            request.session['ErrorList'].append(DocError(errornum, "Неподходящий размер нижнего поля страницы", 'Нижнее поле должно равняться ' + str(request.session['FDown']) + ' см. У вас нижнее поле равняется ' + str(round(float(value)/twipsInSM, 1)) + ' см.', '', '').serialize())
        if name == "w:left" and round(float(value)/twipsInSM, 1) != request.session['FLeft']:
            errornum += 1
            request.session['ErrorList'].append(DocError(errornum, "Неподходящий размер левого поля страницы", 'Левое поле должно равняться ' + str(request.session['FLeft']) + ' см. У вас левое поле равняется ' + str(round(float(value)/twipsInSM, 1)) + ' см.', '', '').serialize())
        if name == "w:right" and round(float(value)/twipsInSM, 1) != request.session['FRight']:
            errornum += 1
            request.session['ErrorList'].append(DocError(errornum, "Неподходящий размер правого поля страницы", 'Правое поле должно равняться ' + str(request.session['FRight']) + ' см. У вас правое поле равняется ' + str(round(float(value)/twipsInSM, 1)) + ' см.', '', '').serialize())

    with open(html_path, "r") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'lxml')
        tags = soup.find_all()
        pars = soup.find_all("p")
        chapters = [[soup.new_tag("div")]]
        chapters[0][0].string = "[Начало документа]"
        currentChapter = 0

        styles = str(soup.find_all("style")[0])
        styleMsoNormalStart = styles.find("p.MsoNormal")
        endCh = styleMsoNormalStart
        styleMsoNormal = ""
        df = ""
        ds = ""
        da = ""
        if styleMsoNormalStart >= 0:
            while styles[endCh] != '}':
                if styles[endCh] == '{':
                    styleMsoNormalStart = endCh
                endCh += 1
            styleMsoNormal = styles[styleMsoNormalStart+1 : endCh]
        if styleMsoNormal != "":
            styleAttrs = re.split(";|,", styleMsoNormal.replace('\n', "").replace('\t', ""))
            for attr in styleAttrs:
                if attr[:11] == "font-family":
                    df = attr[12:]
                    df = df.replace('"', "")
                    #print(df)
                if attr[:9] == "font-size":
                    ds = attr[10:]
                    if ds.find('cm') != -1:
                        ds = ds[:ds.find('cm')]
                    if ds.find('in') != -1:
                        ds = ds[:ds.find('in')]
                    if ds.find('pt') != -1:
                        ds = ds[:ds.find('pt')]
                    #print(ds)
                if attr[:10] == "text-align":
                    da = attr[11:]
                    da = da.replace('"', "")
                    #print(da)
            #print(styleAttrs)

        #print(styleMsoNormal)

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
                    #print("gotcha")
                    chapters.append([])
                    currentChapter += 1
                    chapters[currentChapter].append(tag)
                    isHeader = True
                spanChild = None
                try:
                    if len(list(list(tag.children)[0].children)) > 0:
                        #print(list(list(tag.children)[0].children))
                        pass
                except:
                    pass
                #if (str(tag).find("<![if !supportLists]>")):
                    #print(str(tag))
                tagSoup = BeautifulSoup(str(tag).replace('●', "").replace('○', "") , "lxml")
                spanTag = tagSoup.find_all("span")
                #print(len(list(spanTag)))
                for child in spanTag:
                    if child.name == "span" and re.search('\S', child.text.replace("<o:p></o:p>", "")) != None:
                        spanChild = child
                        if "style" in spanChild.attrs:
                            #print(child.text + "---------------------")
                            spanAtr = spanChild.attrs["style"]
                            spanStyles = re.split(";|,", spanAtr.replace('\n', ""))
                            isfontNameF = False
                            isfontSizeF = False
                            for spanStyle in spanStyles:
                                #if spanStyle.find("font-family:") != -1:
                                    #ff = spanStyle[spanStyle.find(':') + 1:]
                                if spanStyle[:11] == "font-family":
                                    ff = spanStyle[12:]
                                    ff = ff.replace('\"', "")
                                    isfontNameF = True
                                    #print(ff + " ++++++ " + request.session['FontName'])
                                    if ff != request.session['FontName'] and ff not in ["Symbol", "Wingdings", "Cambria Math"]:
                                        if errornum != 0:
                                            lastError = request.session['ErrorList'][errornum-1]
                                            if not (lastError['errorType'] == "Неподходящий шрифт" and  lastError['errorDisc'] == 'Должен быть шрифт "' + request.session['FontName'] + '". У вас стоит шрифт "' + ff + '".' and lastError['chapter'] == chapters[currentChapter][0].text and lastError['text'] == tag.text):
                                                errornum += 1
                                                request.session['ErrorList'].append(DocError(errornum, "Неподходящий шрифт", 'Должен быть шрифт "' + request.session['FontName'] + '". У вас стоит шрифт "' + ff + '".', chapters[currentChapter][0].text, tag.text).serialize())
                                        else:
                                            errornum += 1
                                            request.session['ErrorList'].append(DocError(errornum, "Неподходящий шрифт", 'Должен быть шрифт "' + request.session['FontName'] + '". У вас стоит шрифт "' + ff + '".', chapters[currentChapter][0].text, tag.text).serialize())
                                #if spanStyle.find("font-size:") != -1:
                                    #fs = spanStyle[spanStyle.find(':') + 1:]
                                if spanStyle[:9] == "font-size":
                                    fs = spanStyle[10:]
                                    #fs = fs[:fs.find('.')]
                                    if fs.find('cm') != -1:
                                        fs = fs[:fs.find('cm')]
                                    if fs.find('in') != -1:
                                        fs = fs[:fs.find('in')]
                                    if fs.find('pt') != -1:
                                        fs = fs[:fs.find('pt')]
                                    isfontSizeF = True
                                    #print(str(float(fs)) + " ====== " + str(float(request.session['FontSize'])))
                                    if float(fs) != float(request.session['FontSize']):
                                        if errornum != 0:
                                            lastError = request.session['ErrorList'][errornum-1]
                                            if not (lastError['errorType'] == "Неподходящий размер шрифта" and  lastError['errorDisc'] == 'Размер шрифта должен быть равен "' + str(request.session['FontSize']) + '". У вас размер шрифта равен "' + str(fs) + '".' and lastError['chapter'] == chapters[currentChapter][0].text and lastError['text'] == tag.text):
                                                errornum += 1
                                                request.session['ErrorList'].append(DocError(errornum, "Неподходящий размер шрифта", 'Размер шрифта должен быть равен "' + str(request.session['FontSize']) + '". У вас размер шрифта равен "' + str(fs) + '".', chapters[currentChapter][0].text, tag.text).serialize())
                                        else:
                                            errornum += 1
                                            request.session['ErrorList'].append(DocError(errornum, "Неподходящий размер шрифта", 'Размер шрифта должен быть равен "' + str(request.session['FontSize']) + '". У вас размер шрифта равен "' + str(fs) + '".', chapters[currentChapter][0].text, tag.text).serialize())
                            if not isfontNameF:
                                if df != request.session['FontName']:
                                    if errornum != 0:
                                        lastError = request.session['ErrorList'][errornum-1]
                                        if not (lastError['errorType'] == "Неподходящий шрифт" and  lastError['errorDisc'] == 'Должен быть шрифт "' + request.session['FontName'] + '". У вас стоит шрифт "' + df + '".' and lastError['chapter'] == chapters[currentChapter][0].text and lastError['text'] == tag.text):
                                            errornum += 1
                                            request.session['ErrorList'].append(DocError(errornum, "Неподходящий шрифт", 'Должен быть шрифт "' + request.session['FontName'] + '". У вас стоит шрифт "' + df + '".', chapters[currentChapter][0].text, tag.text).serialize())
                                    else:
                                        errornum += 1
                                        request.session['ErrorList'].append(DocError(errornum, "Неподходящий шрифт", 'Должен быть шрифт "' + request.session['FontName'] + '". У вас стоит шрифт "' + df + '".', chapters[currentChapter][0].text, tag.text).serialize())
                            if not isfontSizeF:
                                if float(ds) != float(request.session['FontSize']):
                                    if errornum != 0:
                                        lastError = request.session['ErrorList'][errornum-1]
                                        if not (lastError['errorType'] == "Неподходящий размер шрифта" and  lastError['errorDisc'] == 'Размер шрифта должен быть равен "' + str(request.session['FontSize']) + '". У вас размер шрифта равен "' + str(ds) + '".' and lastError['chapter'] == chapters[currentChapter][0].text and lastError['text'] == tag.text):
                                            errornum += 1
                                            request.session['ErrorList'].append(DocError(errornum, "Неподходящий размер шрифта", 'Размер шрифта должен быть равен "' + str(request.session['FontSize']) + '". У вас размер шрифта равен "' + str(ds) + '".', chapters[currentChapter][0].text, tag.text).serialize())
                                    else:
                                        errornum += 1
                                        request.session['ErrorList'].append(DocError(errornum, "Неподходящий размер шрифта", 'Размер шрифта должен быть равен "' + str(request.session['FontSize']) + '". У вас размер шрифта равен "' + str(ds) + '".', chapters[currentChapter][0].text, tag.text).serialize())

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
                            '''if parStyle.find('margin-top:') != -1:
                                mt = parStyle[parStyle.find(':') + 1:]
                                mt = mt[:mt.find('.')]
                                if float(mt) != request.session['LineSpace'] and float(mt) != 0:
                                    errornum += 1
                                    request.session['ErrorList'].append(DocError(errornum, "Неподходящий межстрочный интервал", 'Межстрочный интервал должен быть равен "' + str(request.session['LineSpace']) + '". У вас межстрочный интервал равен "' + str(mt) + '".', chapters[currentChapter][0].text, tag.text).serialize())
                                # print("mt:" + mt)'''

                            if parStyle.find('text-align:') != -1 and currentChapter > 0 and re.search('^(.+) (\d+).', tag.text) == None:
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
                            elif da != request.session['TextAlign']:
                                textAl = ""
                                textAlTrue = ""
                                if da == "justify":
                                    textAl = "по ширине"
                                elif da == "center":
                                    textAl = "по центру"
                                elif da == "left":
                                    textAl = "по левой стороне"
                                elif da == "right":
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
                                
                            '''if parStyle.find('text-indent:') != -1:
                                ti = parStyle[parStyle.find(':') + 1:]
                                if ti.find('.') != -1:
                                    ti = ti[:ti.find('.')]
                                if ti.find('cm') != -1:
                                    ti = ti[:ti.find('cm')]
                                if float(ti) != request.session['ParIndent'] and float(ti) > 0:
                                    errornum += 1
                                    request.session['ErrorList'].append(DocError(errornum, "Неподходящий абзацный отступ", 'Абзацный отступ должен быть равен "' + str(request.session['ParIndent']) + '". У вас абзацный отступ равен "' + str(ti) + '".', chapters[currentChapter][0].text, tag.text).serialize())
                                # print("ti:" + ti)'''
        
            if isHeader:
                #print(tag.text + "--------------" + str(len(tag.text)))
                if tag.text[len(tag.text) - 1] == '.':
                        if errornum != 0:
                            lastError = request.session['ErrorList'][errornum-1]
                            if not (lastError['errorType'] == "Точка в конце названия главы" and  lastError['errorDisc'] == 'В конце названия главы не должно быть точки' and lastError['chapter'] == chapters[currentChapter][0].text and lastError['text'] == tag.text):
                                errornum += 1
                                request.session['ErrorList'].append(DocError(errornum, "Точка в конце названия главы", 'В конце названия главы не должно быть точки', chapters[currentChapter][0].text, tag.text).serialize())
                        else:
                            errornum += 1
                            request.session['ErrorList'].append(DocError(errornum, "Точка в конце названия главы", 'В конце названия главы не должно быть точки', chapters[currentChapter][0].text, tag.text).serialize())
        
        #print(len(chapters))
        for ch in chapters:
            #print(ch[0].text)
            #print("---------------------------------------------------------------------------")
            if ch[0].text[len(ch[0].text) - 1] == '.':
                chaptersHave.append(ch[0].text[:-1])
            else:
                chaptersHave.append(ch[0].text)
        for ch in chaptersStr:
            if not ((ch == 'Содержание' and ('Оглавление' in chaptersHave or 'Содержание' in chaptersHave)) or ch in chaptersHave):
                if errornum != 0:
                    lastError = request.session['ErrorList'][errornum-1]
                    if not (lastError['errorType'] == "Отсутствует необходимая глава" and  lastError['errorDisc'] == 'У вас нет необходимой главы "'+ch+'"' and lastError['chapter'] == '' and lastError['text'] == ''):
                        errornum += 1
                        request.session['ErrorList'].append(DocError(errornum, "Отсутствует необходимая глава", 'У вас нет необходимой главы "'+ch+'"', '', '').serialize())
                else:
                    errornum += 1
                    request.session['ErrorList'].append(DocError(errornum, "Отсутствует необходимая глава", 'У вас нет необходимой главы "'+ch+'"', '', '').serialize())
    
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
    if 'Struct2' not in request.session:
        request.session['Struct2'] = True
    if 'Struct3' not in request.session:
        request.session['Struct3'] = True
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

    if request.method == 'POST':
        request.session['TemplateName'] = request.POST['TemplateName']
        request.session['FontSize'] = request.POST['FontSize']
        request.session['FontName'] = request.POST['FontName']
        request.session['TextAlign'] = request.POST['TextAlign']
        request.session['FLeft'] = request.POST['FLeft']
        request.session['FRight'] = request.POST['FRight']
        request.session['FUp'] = request.POST['FUp']
        request.session['FDown'] = request.POST['FDown']
        if 'Struct2' in request.POST:
            request.session['Struct2'] = True
        else:
            request.session['Struct2'] = False
        if 'Struct3' in request.POST:
            request.session['Struct3'] = True
        else:
            request.session['Struct3'] = False
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

        WCTFile = open(os.getcwd()+'\\WCT\\'+request.session['TemplateName']+'.wct', 'w')
        WCTFile.write(request.session['TemplateName']+'\n')
        WCTFile.write(request.session['FontSize']+'\n')
        WCTFile.write(request.session['FontName']+'\n')
        WCTFile.write(request.session['TextAlign']+'\n')
        WCTFile.write(request.session['FLeft']+'\n')
        WCTFile.write(request.session['FRight']+'\n')
        WCTFile.write(request.session['FUp']+'\n')
        WCTFile.write(request.session['FDown']+'\n')
        WCTFile.write(str(int(request.session['Struct2']))+str(int(request.session['Struct3']))+str(int(request.session['Struct5']))+str(int(request.session['Struct6']))+str(int(request.session['Struct7']))+str(int(request.session['Struct8']))+str(int(request.session['Struct9']))+str(int(request.session['Struct10']))+'\n')
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
       
    if 'FontSize' not in request.session:
        request.session['TemplateName'] = "Отчет по курсовой работе"
        request.session['FontSize'] = 14
        request.session['FontName'] = 'Times New Roman'
        request.session['TextAlign'] = 'justify'
        request.session['FLeft'] = 3
        request.session['FRight'] = 1
        request.session['FUp'] = 2
        request.session['FDown'] = 2
        request.session['Structs'] = '11110000'
    
    chaptersStr = []
    for i in range(0, 8):
        if str(request.session['Structs'])[i] == '1':
            if i == 0:
                chaptersStr.append('Содержание/Оглавление')
            elif i == 1:
                chaptersStr.append('Введение')
            elif i == 2:
                chaptersStr.append('Заключение')
            elif i == 3:
                chaptersStr.append('Список литературы')
            elif i == 4:
                chaptersStr.append('Словарь сокращений')
            elif i == 5:
                chaptersStr.append('Словарь терминов')
            elif i == 6:
                chaptersStr.append('Список иллюстрированного материала')
            elif i == 7:
                chaptersStr.append('Приложения')
    
    textAl = ""
    if request.session['TextAlign'] == "justify":
        textAl = "По ширине"
    elif request.session['TextAlign'] == "center":
        textAl = "По центру"
    elif request.session['TextAlign'] == "left":
        textAl = "По левой стороне"
    elif request.session['TextAlign'] == "right":
        textAl = "По правой стороне"
    else:
        textAl = "неизвестным образом"
    
    context = {
        "TemplateName": request.session['TemplateName'],
        "FontSize": request.session['FontSize'],
        "FontName": request.session['FontName'],
        "TextAlign": textAl,
        "FLeft": request.session['FLeft'],
        "FRight": request.session['FRight'],
        "FUp": request.session['FUp'],
        "FDown": request.session['FDown'],
        "Chapters": chaptersStr,
        "ErrorList": request.session['ErrorList']
    }

    return render(request, 'errors.html', context)

def main(request):
    return redirect('checker')