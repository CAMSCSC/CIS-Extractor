import pdfplumber
from pdfminer.layout import LTChar
from typing import List, Tuple
import os 
import shutil
import tabulate
pdf = pdfplumber.open('CIS-windows.pdf')

shutil.rmtree("./MD-files-windows")
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

    # Get pdf page as char list (contains font info)
    chars: List[LTChar] = page.chars
    # True if font is CourierNewPSMT (code block font)
    monospaceFontIndices: List[bool] = [chars[i]["fontname"] ==
                                        "ABCDEE+CourierNewPSMT" for i in range(len(chars))]
    
    # Re-generate text using chars
    text = "".join([char["text"] for char in chars])
    
    codeIndices = getTrueRanges(monospaceFontIndices)
    text = addFormat(text, codeIndices, "`")
    
    remediationStart = text.find("Remediation:") + 13
    remediationEnd = text.find("Default Value:")
    if remediationEnd != -1:
        return text[remediationStart : remediationEnd]
    else:
        return text[remediationStart : len(text)]


def getTrueRanges(list: List[bool]) -> 'List[Tuple[int, int]]':
    """ Returns the ranges of true values in a boolean list.
    """
    indiceRanges: 'List[Tuple[int, int]]' = []
    
    alreadyCheckedIndices: int = -1
    for index, item in enumerate(list):
        # Skip if already checked
        if index <= alreadyCheckedIndices:
            continue
        # Check for true values after the item if item is true
        if item == None:
            continue
        if item:
            for index2, item2 in enumerate(list[index::]):
                index2 += index
                if item2 == None:
                    continue
                # Once the value is not true, return the range up to 1 index lower than it
                if not item2:
                    indiceRanges.append((index, index2 - 1))
                    alreadyCheckedIndices = index2 - 1
                    break
            # if the end of the list is reached, return index to end
            else:
                # Note: for-else behavior might break in future versions of python
                indiceRanges.append((index, len(list) - 1))
                return indiceRanges
    
    return indiceRanges

def addFormat(text: str, codeIndices: 'List[Tuple[int, int]]', formatChar: str) -> str:
    """ Format text as code blocks or bolds by adding ` or * to the start and end
    """
    textArr: List[str] = [char for char in text]
    for index, codeBlock in enumerate(codeIndices):
         
        textArr.insert(codeBlock[0] + 2*index, formatChar)
        textArr.insert(codeBlock[1] + 2*index + 2, formatChar)

    return "".join(textArr)

sectionFilesWritten = []

def writeToFile(sectionNum: int, remediation: str):
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
    file.write("\n" + remediation.replace("\u25cf", "").replace("\uf0b7", ""))
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