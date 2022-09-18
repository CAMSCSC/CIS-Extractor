import pdfplumber

pdf = pdfplumber.open('CIS.pdf')

file1 = open("MyFile.txt","a")


def findSectionNumber(text):
    if text[2].isdigit() == True:
        sectionNumber = ""
        i = 2
        while text[i] != " ":
            sectionNumber += text[i]
            i += 1
        return sectionNumber
    else:
        return False

def findRemediation(text, pgNumber):
    if text.find("Remediation:") != -1:
        remediationStart = text.find("Remediation:") + 14
        remediationEnd = text.find("Default Value:")
        if remediationEnd != -1:
           return text[remediationStart : remediationEnd]
        else:
           return text[remediationStart : len(text) - 13 - len(str(pgNumber))] # 13 is some random number to get rid of the page number could be wrong idk
    else:
        return False

for i in range(55,1196): # in practice should be up to 1196
    page = pdf.pages[i]
    text = page.extract_text()
    
    if findSectionNumber(text) != False:
        file1.write("Section " + findSectionNumber(text))
        # print(findSectionNumber(text))
    if findRemediation(text, i) != False:
        file1.write("\n" + findRemediation(text, i))
        # print(findRemediation(text, i))

file1.close()