# This module is used for extracting the remainder of the student
# information that can't be obtained within the first page 
# of the Transcript File

import sys 
import threading
from typing import Union

# These variables need to be global, and thankfully they have no affect to the program
_splitterFlag = False 
_upperDivisonCredits = 0.00 

def trackCumulativeInformation(text, cumulativeInformation):
    global _splitterFlag, _upperDivisonCredits
    # To determine if we are looking at a class category, we need to see if our line of Information
    # is at a specific semester (Fall, Spring, etc) 
    for findSemester in text: #Iterating over a list
        modifiedLine = findSemester.replace(" ", "") # Create a line with no whitespace 
        if _splitterFlag == True:
            indexLocation = text.index(findSemester)
            slicedTextList = text[indexLocation::]
            floatOrBoolValue = findUpperDivisonCreditsWithinSemester(slicedTextList)
            if isinstance(floatOrBoolValue, float):
                _splitterFlag = False #Reset the global variable back to its original phase 
                _upperDivisonCredits = _upperDivisonCredits + floatOrBoolValue
            elif isinstance(floatOrBoolValue, bool): #We have discovered that the transcript, is split, so we need to go on to the next page 
                _splitterFlag = True 
        if "UndergraduateCareerTotals" in modifiedLine: #Tells us we have reached the end of the transcript
            indexLocation = text.index(findSemester)
            handleCumulativeCreditsandGPA(text[indexLocation + 1], cumulativeInformation)
            return cumulativeInformation # Exit the program
        if ("Fall" in modifiedLine or "Spring" in modifiedLine or "Winter" in modifiedLine or "Summer" in modifiedLine) and "Session" not in modifiedLine: #There is also a chance that the transcript page gets cut off and the classes are in the next page, so we need to handle that
            indexLocation = text.index(findSemester)
            slicedTextList = text[indexLocation::] 
            floatOrBoolValue = findUpperDivisonCreditsWithinSemester(slicedTextList)
            if isinstance(floatOrBoolValue, float):
                _splitterFlag = False #Reset the global variable back to its original phase 
                _upperDivisonCredits = _upperDivisonCredits + floatOrBoolValue
            elif isinstance(floatOrBoolValue, bool): #We have discovered that the transcript, is split, so we need to go on to the next page 
                _splitterFlag = True 
    # This part of the program is reached when we have reached the end of this part of the PDF page
    cumulativeInformation['Upper Division Credits'] = _upperDivisonCredits 

    
@staticmethod
def findUpperDivisonCreditsWithinSemester(text) -> Union[float, bool]:
    upperDivisonCreditsCounter = 0.000
    for findClasses in text:
        modifiedClassLine = findClasses.replace(" ", "")
        if "TermGPA" in modifiedClassLine: # Signifies the end of the semester
            return upperDivisonCreditsCounter
        classNumberof3 = modifiedClassLine[3:6] #We only need to check a certain parameter like this (this may also lead to potential of bugs but we will try to circumvent this in the future)
        try:
            if int(classNumberof3) >= 300:
                modifiedClassLine = modifiedClassLine[6::]
                creditsValue = validateUpperClassCredits(findClasses) # We send in the regular text 
                upperDivisonCreditsCounter += creditsValue
        except: pass
    return True

@staticmethod
def validateUpperClassCredits(modifiedClassLine) -> float:
    indexCounter = 0
    creditsEarned = ""
    while not (modifiedClassLine[indexCounter] >= '0' and modifiedClassLine[indexCounter] <= '9'): indexCounter += 1
    while (modifiedClassLine[indexCounter] >= '0' and modifiedClassLine[indexCounter] <= '9') or modifiedClassLine[indexCounter] == '.': indexCounter += 1
    while not (modifiedClassLine[indexCounter] >= '0' and modifiedClassLine[indexCounter] <= '9'): indexCounter += 1
    while (modifiedClassLine[indexCounter] >= '0' and modifiedClassLine[indexCounter] <= '9') or modifiedClassLine[indexCounter] == '.': 
        creditsEarned += modifiedClassLine[indexCounter]
        indexCounter += 1
    try:
        if float(creditsEarned) != 0.000: return float(creditsEarned)
    except:
        sys.exit("Could not determine the credits earned. Invalid PDF File. Exiting Program")
    return 0.000



@staticmethod
def handleCumulativeCreditsandGPA(text, cumulativeInformation) -> dict:
    thread1 = threading.Thread(target=cumulativeGPAThread, args=(text, cumulativeInformation))
    thread2 = threading.Thread(target=cumulativeCreditsThread, args=(text, cumulativeInformation))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    return cumulativeInformation


@staticmethod
def cumulativeGPAThread(text, cumulativeInformation):
    indexLocation = text.index("Cum GPA:")
    gpaString = ""
    while not (text[indexLocation] >= '0' and text[indexLocation] <= '9'): indexLocation += 1
    while (text[indexLocation] >= '0' and text[indexLocation] <= '9') or text[indexLocation] == '.':
        gpaString += text[indexLocation]
        indexLocation += 1
    cumulativeInformation['Cumulative GPA'] = gpaString 


@staticmethod
def cumulativeCreditsThread(text, cumulativeInformation): # We will send in an unmodified text to deal with this 
    indexLocation = text.index("Cum Totals") 
    cumulativeCreditsString = ""
    while not (text[indexLocation] >= '0' and text[indexLocation] <= '9'): indexLocation += 1
    while (text[indexLocation] >= '0' and text[indexLocation] <= '9') or text[indexLocation] == '.': indexLocation += 1
    while not (text[indexLocation] >= '0' and text[indexLocation] <= '9'): indexLocation += 1
    while (text[indexLocation] >= '0' and text[indexLocation] <= '9') or text[indexLocation] == '.': 
        cumulativeCreditsString += text[indexLocation]
        indexLocation += 1
    cumulativeInformation['Cumulative Credits'] = cumulativeCreditsString

def resetGlobalVariablesForCumulativeInformation():
    global _splitterFlag, _upperDivisonCredits
    _splitterFlag = False 
    _upperDivisonCredits = 0.00
    