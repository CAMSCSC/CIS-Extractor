import pdfplumber
import os 
pdf = pdfplumber.open('CIS-windows.pdf')

os.remove("MD-files-windows")
os.mkdir("MD-files-windows")

def getSectionNumber(pgNumber):
    page = pdf.pages[pgNumber]
    text = page.extract_text()
    if text[2].isdigit() == True:
        sectionNumber = ""
        i = 2
        while text[i] != " ":
            sectionNumber += text[i]
            i += 1
        return sectionNumber
    else:
        return False

def getRemediation(pgNumber):
    
    page = pdf.pages[pgNumber]
    text = page.extract_text()

    while text.find("Remediation:") == -1:
        pgNumber += 1
        page = pdf.pages[pgNumber]
        text = page.extract_text()
        if text[2].isdigit() == True:
            return False # end the function if there is no remediation for that page number section
    # find page number where there is a remediation for the section

    remediationStart = text.find("Remediation:") + 14
    remediationEnd = text.find("Default Value:")
    if remediationEnd != -1:
        return text[remediationStart : remediationEnd]
    else:
        return text[remediationStart : len(text) - 14 - len(str(pgNumber))] # 13 is some random number to get rid of the page number could be wrong idk

sectionFilesWritten = []

def writeToFile(sectionNum, remediation):
    numOfPeriods = 0
    fileSectionNumber = ""
    folderSectionNumber = ""

    for char in sectionNum:
        if char == ".":
            numOfPeriods += 1
            if numOfPeriods == 2:
                break
        fileSectionNumber += char

    for char in sectionNum:
        if char == ".":
            break
        folderSectionNumber += char

    file = open("./MD-files-windows/" + folderSectionNumber + "/" + fileSectionNumber + ".md","a")
    file.write("\n" + "### " + sectionNum + "  ")
    file.write("\n" + remediation)
    file.close()

    file2 = open("./MD-files-windows/" + folderSectionNumber + ".md", "a+")
    if not fileSectionNumber in sectionFilesWritten:
        file2.write("\n" + "## " + fileSectionNumber + "  ")
        file2.write("\n ```{include} ./" + folderSectionNumber + "/" + fileSectionNumber + ".md" + "\n ``` \n")
        sectionFilesWritten.append(fileSectionNumber)
    file2.close()


for i in range(1,20):
    os.mkdir("./MD-files-windows/" + str(i)) # make folders for placing MD files

for pageNumber in range(55,1196): # in practice should be up to 1196
    if getSectionNumber(pageNumber) != False and getRemediation(pageNumber) != False: # if the section number exists on that page, and that section has a remediation
        writeToFile(getSectionNumber(pageNumber), getRemediation(pageNumber))