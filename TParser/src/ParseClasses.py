# The purpose of this module is to parse the classes
# that we come across when we traverse through the PDF file

from UniversalClassObject import *
from MinimalClassObject import *
from SBCClassObject import * 
import sys

#This will most likely be our longest function 

#The responsibility of this method is to track ONLY the upperdivison CSE courses and the lower divison CSE courses the student is taking 
def majorClassTracker(text, upperDivisionCourses, lowerDivisionCourses, technicalCourses):
    # We want our dictionary to hold UpperDivision class objects in the upperDivisonCourse dictionary
    # and we want our dictionary to hold LowerDivision class objects in the lowerDivisonCourses dictionary
    requiredLowerDivisonCourses = ("114", "214", "215", "216", "220")
    requiredUpperDivisionCourses = ("303", "312", "300", "310", "316", "320", "373", "416")
    semesterText = ""
    semesterYear = ""
    for lineOfInformation in text:
        modifiedLine = lineOfInformation.replace(" ", "")
        if "TermGPA" in modifiedLine: # Reset the semesterText and semesterYear strings 
            semesterText = ""
            semesterYear = ""
        if ("Spring" in modifiedLine or "Fall" in modifiedLine or "Winter" in modifiedLine or "Summer" in modifiedLine) and ("Session" not in modifiedLine):
            index = 0
            while not (modifiedLine[index] >= '0' and modifiedLine[index] <= '9'):
                semesterText += modifiedLine[index]
                index += 1
            while (index != len(modifiedLine) and modifiedLine[index] >= '0' and modifiedLine[index] <= '9'):
                semesterYear += modifiedLine[index]
                index += 1
        if ("Spring" in modifiedLine or "Fall" in modifiedLine or "Winter" in modifiedLine or "Summer" in modifiedLine) and ("Session" in modifiedLine) and (semesterText == "") and (semesterYear == ""):
            springIndex = modifiedLine.find("Spring")
            fallIndex = modifiedLine.find("Fall")
            winterIndex = modifiedLine.find("Winter")
            summerIndex = modifiedLine.find("Summer")
            if springIndex >= 0:
                semesterText = "Spring"
            elif fallIndex >= 0:
                semesterText = "Fall"
            elif winterIndex >= 0:
                semesterText = "Winter"
            elif summerIndex >= 0:
                semesterText = "Summer"
            findFirstCharacter = modifiedLine.find("/")
            stringAfter = modifiedLine[findFirstCharacter+1::]
            findSecondCharacter = stringAfter.find("/")
            stringAfterSecond = stringAfter[findSecondCharacter+1::]
            index = 0
            while (stringAfterSecond[index] >= '0' and stringAfterSecond[index] <= '9'):
                semesterYear += stringAfterSecond[index]
                index += 1
        if "CSE" in modifiedLine:
            indexLocation = modifiedLine.index("CSE") + 3
            classNumber = ""
            while len(classNumber) != 3:
                classNumber += modifiedLine[indexLocation]
                indexLocation += 1
            try:
                int(classNumber)
                if classNumber == "101": continue
                elif classNumber in requiredLowerDivisonCourses:
                    createClassObjetctForCSE(semesterText, semesterYear, modifiedLine[indexLocation::], classNumber, lowerDivisionCourses)
                elif classNumber in requiredUpperDivisionCourses:
                    createClassObjetctForCSE(semesterText, semesterYear, modifiedLine[indexLocation::], classNumber, upperDivisionCourses)
                else: 
                    if classNumber == "495" or classNumber == "496" or classNumber == "475" or classNumber == "301": continue # Won't be counted for credits
                    if (classNumber == "487" and '487' in technicalCourses) or (classNumber == "488" and '488' in technicalCourses): continue # We can only use the class once as a technical elective 
                    createClassObjetctForCSE(semesterText, semesterYear, modifiedLine[indexLocation::], classNumber, technicalCourses) 
            except:
                sys.exit("Trouble reading the data from the file. Exiting Program")
        

def mathTracker(text, mathRequiredCourses):
    semesterText = ""
    semesterYear = ""
    for lineOfInformation in text:
        modifiedLine = lineOfInformation.replace(" ", "")
        if "TermGPA" in modifiedLine or "TestTransGPA" in modifiedLine: # Reset the semesterText and semesterYear strings 
                semesterText = ""
                semesterYear = ""
        if ("Spring" in modifiedLine or "Fall" in modifiedLine or "Winter" in modifiedLine or "Summer" in modifiedLine) and "Session" not in modifiedLine:
                index = 0
                while not (modifiedLine[index] >= '0' and modifiedLine[index] <= '9'):
                    semesterText += modifiedLine[index]
                    index += 1
                while (index != len(modifiedLine) and modifiedLine[index] >= '0' and modifiedLine[index] <= '9'):
                    semesterYear += modifiedLine[index]
                    index += 1
        if ("Spring" in modifiedLine or "Fall" in modifiedLine or "Winter" in modifiedLine or "Summer" in modifiedLine) and ("Session" in modifiedLine) and (semesterText == "") and (semesterYear == ""):
            springIndex = modifiedLine.find("Spring")
            fallIndex = modifiedLine.find("Fall")
            winterIndex = modifiedLine.find("Winter")
            summerIndex = modifiedLine.find("Summer")
            if springIndex >= 0:
                semesterText = "Spring"
            elif fallIndex >= 0:
                semesterText = "Fall"
            elif winterIndex >= 0:
                semesterText = "Winter"
            elif summerIndex >= 0:
                semesterText = "Summer"
            findFirstCharacter = modifiedLine.find("/")
            stringAfter = modifiedLine[findFirstCharacter+1::]
            findSecondCharacter = stringAfter.find("/")
            stringAfterSecond = stringAfter[findSecondCharacter+1::]
            index = 0
            while (stringAfterSecond[index] >= '0' and stringAfterSecond[index] <= '9'):
                semesterYear += stringAfterSecond[index]
                index += 1
        if "AMS" in modifiedLine or "MAT" in modifiedLine:
                indexLocation = 0
                classTitle = ""
                if "AMS" in modifiedLine:
                    indexLocation = modifiedLine.index("AMS") + 3
                    classTitle = "AMS"
                elif "MAT" in modifiedLine:
                    indexLocation = modifiedLine.index("MAT") + 3
                    classTitle = "MAT"
                classNumber = ""
                while len(classNumber) != 3:
                    classNumber += modifiedLine[indexLocation]
                    indexLocation += 1
                if classNumber == "LVL": continue # Tells us Math Placement Test, so we skip this 
                try:
                    int(classNumber)
                    createClassObjectForMathCourses(classTitle, semesterText, semesterYear, modifiedLine[indexLocation::], classNumber, mathRequiredCourses)
                except:
                    sys.exit("Trouble reading the data from the file. Exiting Program")
    

def scienceTracker(text, scienceCourses):
    semesterText = ""
    semesterYear = ""
    for lineOfInformation in text:
        modifiedLine = lineOfInformation.replace(" ", "")
        if "TermGPA" in modifiedLine: # Reset the semesterText and semesterYear strings 
                semesterText = ""
                semesterYear = ""
        if ("Spring" in modifiedLine or "Fall" in modifiedLine or "Winter" in modifiedLine or "Summer" in modifiedLine) and ("Session" not in modifiedLine):
                index = 0
                while not (modifiedLine[index] >= '0' and modifiedLine[index] <= '9'):
                    semesterText += modifiedLine[index]
                    index += 1
                while (index != len(modifiedLine) and modifiedLine[index] >= '0' and modifiedLine[index] <= '9'):
                    semesterYear += modifiedLine[index]
                    index += 1
        if ("Spring" in modifiedLine or "Fall" in modifiedLine or "Winter" in modifiedLine or "Summer" in modifiedLine) and ("Session" in modifiedLine) and (semesterText == "") and (semesterYear == ""):
            springIndex = modifiedLine.find("Spring")
            fallIndex = modifiedLine.find("Fall")
            winterIndex = modifiedLine.find("Winter")
            summerIndex = modifiedLine.find("Summer")
            if springIndex >= 0:
                semesterText = "Spring"
            elif fallIndex >= 0:
                semesterText = "Fall"
            elif winterIndex >= 0:
                semesterText = "Winter"
            elif summerIndex >= 0:
                semesterText = "Summer"
            findFirstCharacter = modifiedLine.find("/")
            stringAfter = modifiedLine[findFirstCharacter+1::]
            findSecondCharacter = stringAfter.find("/")
            stringAfterSecond = stringAfter[findSecondCharacter+1::]
            index = 0
            while (stringAfterSecond[index] >= '0' and stringAfterSecond[index] <= '9'):
                semesterYear += stringAfterSecond[index]
                index += 1
        if "PHY" in modifiedLine or "BIO" in modifiedLine or "CHE" in modifiedLine or "GEO" in modifiedLine or "AST" in modifiedLine:
                classTitle = modifiedLine
                indexLocation = 0
                if "PHY" in modifiedLine:
                    indexLocation = modifiedLine.index("PHY") + 3
                    classTitle = "PHY"
                elif "BIO" in modifiedLine:
                    indexLocation = modifiedLine.index("BIO") + 3
                    classTitle = "BIO"
                elif "GEO" in modifiedLine:
                    indexLocation = modifiedLine.index("GEO") + 3
                    classTitle = "GEO"
                elif "AST" in modifiedLine:
                    indexLocation = modifiedLine.index("AST") + 3
                    classTitle = "AST"
                elif "CHE" in modifiedLine:
                    indexLocation = modifiedLine.index("CHE") + 3
                    classTitle = "CHE"
                classNumber = ""
                while len(classNumber) != 3:
                    classNumber += modifiedLine[indexLocation]
                    indexLocation += 1
                try:
                    int(classNumber)
                    createClassObjectForScienceCourses(classTitle, semesterText, semesterYear, modifiedLine[indexLocation::], classNumber, scienceCourses)
                except:
                    sys.exit("Trouble reading the data from the file. Exiting Program")

def sbcsTracker(text, sbcCourses):

    transferEquivalency = {('AFS', 'ECO', 'POL', 'HIS', 'PSY'): 'SBS', ('AFS', 'HIS', 'POL'): 'USA', ('AFS', 'PSY'): 'CER', ('ARH', 'ARS', 'MUS'): 'ARTS', ('BIO', 'CHE', 'SUS', 'PHY'): 'SNW', ('MAT', 'AMS'): 'QPS', ('CHI', 'FRN', 'GER', 'ITL', 'JPN', 'LAT', 'SPN'): 'LANG', ('CHI', 'FRN', 'GER', 'HIS', 'ITL', 'JPN', 'SPN'): 'GLO', ('CHI', 'EGL', 'FRN', 'GER', 'ITL', 'JPN', 'SPN'): 'HUM', ('CSE'): 'TECH', ('LAT'): 'HFA+'}
    
    semesterText = ""
    semesterYear = ""
    semesterDateInfoParsed = False
    keepSkipping = False 
    for lineinformation in text:
        modifiedLine = lineinformation.replace(" ", "")
        classInfo = modifiedLine[0:3]
        if "TestCredits" in modifiedLine and keepSkipping == False:
            indexOfUnmodifiedLine = text.index(lineinformation)
            listAfterwards = text[indexOfUnmodifiedLine+2::]
            handleTestCreditsSbcs(listAfterwards, sbcCourses, transferEquivalency)
            keepSkipping = True
        if "TestTransGPA" in modifiedLine:
            keepSkipping = False
        if "TermGPA" in modifiedLine:
            semesterText = ""
            semesterYear = ""
            semesterDateInfoParsed = False
        if ("Spring" in modifiedLine or "Fall" in modifiedLine or "Winter" in modifiedLine or "Summer" in modifiedLine) and ("Session" not in modifiedLine) and semesterDateInfoParsed == False:
                index = 0
                while not (modifiedLine[index] >= '0' and modifiedLine[index] <= '9'):
                    semesterText += modifiedLine[index]
                    index += 1
                while (index != len(modifiedLine) and modifiedLine[index] >= '0' and modifiedLine[index] <= '9'):
                    semesterYear += modifiedLine[index]
                    index += 1
                semesterDateInfoParsed = True
        if ("Spring" in modifiedLine or "Fall" in modifiedLine or "Winter" in modifiedLine or "Summer" in modifiedLine) and ("Session" in modifiedLine) and (semesterText == "") and (semesterYear == ""):
            springIndex = modifiedLine.find("Spring")
            fallIndex = modifiedLine.find("Fall")
            winterIndex = modifiedLine.find("Winter")
            summerIndex = modifiedLine.find("Summer")
            if springIndex >= 0:
                semesterText = "Spring"
            elif fallIndex >= 0:
                semesterText = "Fall"
            elif winterIndex >= 0:
                semesterText = "Winter"
            elif summerIndex >= 0:
                semesterText = "Summer"
            findFirstCharacter = modifiedLine.find("/")
            stringAfter = modifiedLine[findFirstCharacter+1::]
            findSecondCharacter = stringAfter.find("/")
            stringAfterSecond = stringAfter[findSecondCharacter+1::]
            index = 0
            while (stringAfterSecond[index] >= '0' and stringAfterSecond[index] <= '9'):
                semesterYear += stringAfterSecond[index]
                index += 1
        elif keepSkipping == False:
            checkSubString = modifiedLine[3:6]
            try: 
                int(checkSubString)
            except: 
                continue

            offsetIndex = 1
            getIndex = text.index(lineinformation)
            lengthCounter = getIndex + 1 # Gets the actual current length of the list, so lengthCounter will always be 1 greater than the index we are accessing
            attributesLine = False
            notFound = False
            attributesLineInfo = ""

            while notFound == False and attributesLine == False and lengthCounter < len(text):
                lengthCounter += 1
                nextLine = text[getIndex+offsetIndex] 
                modifiedNextLine = nextLine.replace(" ", "")
                # check and see if we are reading a class line
                classInfoTemp = modifiedNextLine[3:6]
                if "CourseAttributes" in modifiedNextLine:
                    attributesLineInfo = nextLine
                    attributesLine = True # We found the attributesLine
                elif "TermGPA" in modifiedNextLine and attributesLine == False:
                    notFound = True
                else:
                    offsetIndex += 1
                    try:
                        int(classInfoTemp)
                        notFound = True
                    except:
                        continue # We continue with iteration
            # Once we have found the line with the course attribute, we want to parse it 
            if notFound == True: continue

            if attributesLine == True:
                if "Controlled Access" in attributesLineInfo:
                    # Then we still need to keep looking for the actual line that contains the SBC
                    # Go to the next line:
                    # 1) Next line will have the SBC we are looking for
                    # 2) Next line will be another class, which in that case, we don't create an object
                    controlledAccessLine = text.index(attributesLineInfo)
                    nextLine = text[controlledAccessLine + 1]
                    checkForClass = nextLine[3:6]
                    try: #If this is an integer, then no SBC object will be created
                        int(checkForClass)
                        continue # Means we are looking at a new class line, so we continue
                    except:
                        # This line is an SBC, so we can parse
                        index = 0
                        sbcStringList = []
                        sbcLine = ""
                        while nextLine[index] >= 'A'and nextLine[index] <= 'Z':
                            sbcLine += nextLine[index]
                            index += 1
                        sbcStringList.append(sbcLine)
                        
                        # Might be more SBCs after this, so we need to continue parsing further

                        offsetIndex += 2
                        stillParsingSbcs = False
                        while stillParsingSbcs == False:
                            furtherLine = text[getIndex+offsetIndex] 
                            furtherLineModified = furtherLine.replace(" ", "")
                            # Check to see if there is also a class character or not 
                            classInfoMoreTemp = furtherLineModified[3:6]
                            if "TermGPA" in furtherLineModified:
                                stillParsingSbcs = True 
                            else:
                                try:
                                    int(classInfoMoreTemp)
                                    stillParsingSbcs = True # Set to True
                                except:
                                    offsetIndex += 1
                                    # We have found a line that contains another SBC, so we need to parse this line as well
                                    startingIndexTemp = 0
                                    sbcStringTemp = ""
                                    while furtherLine[startingIndexTemp] != ' ':
                                        sbcStringTemp += furtherLine[startingIndexTemp]
                                        startingIndexTemp += 1
                                    sbcStringList.append(sbcStringTemp)
                        if '' in sbcStringList:
                            indexOfEmpty = sbcStringList.index('')
                            sbcStringList = sbcStringList[0:indexOfEmpty]
                    createClassObjectForSBCCourses(classInfo, sbcStringList, semesterText, semesterYear, modifiedLine, checkSubString, sbcCourses)        
                else:
                    colonIndex = attributesLineInfo.index(':')
                    attributesLineInfoModified = attributesLineInfo[colonIndex+2::]
                    sbcStringList = []
                    sbcString = ""
                    startingIndex = 0
                    while attributesLineInfoModified[startingIndex] != ' ':
                        sbcString += attributesLineInfoModified[startingIndex]
                        startingIndex += 1
                    sbcStringList.append(sbcString)

                    # Might be more to parse, so we don't know 
                    offsetIndex += 1
                    lengthCounterTemp = getIndex + offsetIndex + 1
                    stillParsingSbcs = False
                    while stillParsingSbcs == False and lengthCounterTemp < len(text):
                        lengthCounterTemp += 1
                        furtherLine = text[getIndex+offsetIndex]
                        furtherLineModified = furtherLine.replace(" ", "")
                        # Check to see if there is also a class character or not 
                        classInfoMoreTemp = furtherLineModified[3:6]
                        if "TermGPA" in furtherLineModified:
                            stillParsingSbcs = True 
                        else:
                            try:
                                int(classInfoMoreTemp)
                                stillParsingSbcs = True # Set to True
                            except:
                                offsetIndex += 1
                                # We have found a line that contains another SBC, so we need to parse this line as well
                                startingIndexTemp = 0
                                sbcStringTemp = ""
                                while furtherLine[startingIndexTemp] != ' ':
                                    sbcStringTemp += furtherLine[startingIndexTemp]
                                    startingIndexTemp += 1
                                sbcStringList.append(sbcStringTemp)
                    if '' in sbcStringList:
                        indexOfEmpty = sbcStringList.index('')
                        sbcStringList = sbcStringList[0:indexOfEmpty]
                    createClassObjectForSBCCourses(classInfo, sbcStringList, semesterText, semesterYear, modifiedLine, checkSubString, sbcCourses)

def classTracker(text, classesPerSemester): #Responsible for keeping a dictionary of what classes the student is taking per semester

    transferEquivalency = {('AFS', 'ECO', 'POL', 'HIS', 'PSY'): 'SBS', ('AFS', 'HIS', 'POL'): 'USA', ('AFS', 'PSY'): 'CER', ('ARH', 'ARS', 'MUS'): 'ARTS', ('BIO', 'CHE', 'SUS', 'PHY'): 'SNW', ('MAT', 'AMS'): 'QPS', ('CHI', 'FRN', 'GER', 'ITL', 'JPN', 'LAT', 'SPN'): 'LANG', ('CHI', 'FRN', 'GER', 'HIS', 'ITL', 'JPN', 'SPN'): 'GLO', ('CHI', 'EGL', 'FRN', 'GER', 'ITL', 'JPN', 'SPN'): 'HUM', ('CSE'): 'TECH', ('LAT'): 'HFA+'}

    semesterText = ""
    semesterYear = ""
    keepSkipping = False
    for lineofInformation in text:
        modifiedLine = lineofInformation.replace(" ", "")
        classNumberTracker = modifiedLine[3:6]
        if "TestCredits" in modifiedLine and keepSkipping == False:
            indexOfUnmodifiedLine = text.index(lineofInformation)
            listAfterwards = text[indexOfUnmodifiedLine+2::]
            handleTestCreditsNormal(listAfterwards, classesPerSemester, transferEquivalency)
            keepSkipping = True
        if "TestTransGPA" in modifiedLine:
            keepSkipping = False
        if "TermGPA" in modifiedLine:
            semesterText = ""
            semesterYear = ""
        if ("Spring" in modifiedLine or "Fall" in modifiedLine or "Winter" in modifiedLine or "Summer" in modifiedLine) and ("Session" not in modifiedLine) and keepSkipping == False:
                index = 0
                while not (modifiedLine[index] >= '0' and modifiedLine[index] <= '9'):
                    semesterText += modifiedLine[index]
                    index += 1
                while (index != len(modifiedLine) and modifiedLine[index] >= '0' and modifiedLine[index] <= '9'):
                    semesterYear += modifiedLine[index]
                    index += 1
        if ("Spring" in modifiedLine or "Fall" in modifiedLine or "Winter" in modifiedLine or "Summer" in modifiedLine) and ("Session" in modifiedLine) and (semesterText == "") and (semesterYear == "") and keepSkipping == False:
            springIndex = modifiedLine.find("Spring")
            fallIndex = modifiedLine.find("Fall")
            winterIndex = modifiedLine.find("Winter")
            summerIndex = modifiedLine.find("Summer")
            if springIndex >= 0:
                semesterText = "Spring"
            elif fallIndex >= 0:
                semesterText = "Fall"
            elif winterIndex >= 0:
                semesterText = "Winter"
            elif summerIndex >= 0:
                semesterText = "Summer"
            findFirstCharacter = modifiedLine.find("/")
            stringAfter = modifiedLine[findFirstCharacter+1::]
            findSecondCharacter = stringAfter.find("/")
            stringAfterSecond = stringAfter[findSecondCharacter+1::]
            index = 0
            while (stringAfterSecond[index] >= '0' and stringAfterSecond[index] <= '9'):
                semesterYear += stringAfterSecond[index]
                index += 1
        if keepSkipping == False:
            try:
                int(classNumberTracker)
                classTitle = modifiedLine[0:3]
                createClassInformation(classTitle, classNumberTracker, semesterText, semesterYear, modifiedLine, classesPerSemester)
            except:
                continue # We are not looking at a class line, so we continue
        
       
@staticmethod
def createClassObjetctForCSE(semesterText, semesterYear, modifiedLine, classNumber, courseDictionary):
    # We categorize based on lower division class or an upper division class 
    # We look for more information such as the number of credits the class is worth, the classNumber, the grade received, and any comments that are included
    # Technical courses involve 4 upper divison CSE courses but there are certain restructions that we need to keep in mind
    dictInformation = parseSpecificClassInformation("", "", "", modifiedLine)
    # We now have: semeterText, semesterYear, classNumber, classGrade, classCreditsAmount, and creditsIfNeeded
    # Create our class object
    if int(classNumber) < 300:
        stringCarrier = ""
        if int(classNumber) == 114:
            stringCarrier = " (TECH)"
        lowerDivisionObject = UniversalClassObject("CSE " + classNumber + stringCarrier, dictInformation['classGrade'], dictInformation['classCreditsAmount'], semesterText, semesterYear, dictInformation['classComments'] if classNumber not in courseDictionary else courseDictionary[classNumber].comments)
        courseDictionary[classNumber] = lowerDivisionObject
    elif int(classNumber) >= 300:
        stringCarrier = ""
        if int(classNumber) == 300:
            stringCarrier = " (SPK/WRTD)"
        elif int(classNumber) == 312:
            stringCarrier = " (CER/ESI/STAS)"
        elif int(classNumber) == 316:
            stringCarrier = " (ESI/EXP+/SBS+/STEM+)"
        elif int(classNumber) == 416:
            stringCarrier = " (ESI/EXP+/SBS+/STEM+)"
        upperDivisonObject = UniversalClassObject("CSE " + classNumber + stringCarrier if int(classNumber) in [300, 312, 316, 416] else "CSE " + classNumber, dictInformation['classGrade'], dictInformation['classCreditsAmount'], semesterText, semesterYear, dictInformation['classComments'] if classNumber not in courseDictionary else courseDictionary[classNumber].comments)
        courseDictionary[classNumber] = upperDivisonObject

@staticmethod
def handleTestCreditsSbcs(text, sbcCourses, transferEquivalency):
    semesterText = "Transfer"
    semesterYear = "Credits"
    for lineOfInformation in text:
        modifiedLine = lineOfInformation.replace(" ", "")
        if "TestTransGPA" in modifiedLine: break
        classNumberTracker = modifiedLine[3:6] # Find a class number
        try:
            int(classNumberTracker)
            classTitle = modifiedLine[0:3]
            list_of_keys = transferEquivalency.keys()
            list_of_sbcs = []
            for keys in list_of_keys:
                if classTitle in keys:
                    getSBCValue = transferEquivalency[keys]
                    list_of_sbcs.append(getSBCValue)
            if len(list_of_sbcs) != 0:
                createClassObjectForSBCCourses(classTitle, list_of_sbcs, semesterText, semesterYear, modifiedLine, classNumberTracker, sbcCourses)
        except: # This might be incorrect, but we will see
            classTitle = modifiedLine[0:3]
            list_of_keys = transferEquivalency.keys()
            list_of_sbcs = []
            for keys in list_of_keys:
                if classTitle in keys:
                    getSBCValue = transferEquivalency[keys]
                    list_of_sbcs.append(getSBCValue)
            if len(list_of_sbcs) != 0: #Means we found a class that is associated with an SBC
                createClassObjectForSBCCourses(classTitle, list_of_sbcs, semesterText, semesterYear, modifiedLine, classNumberTracker, sbcCourses)   
            continue
           

@staticmethod # We will hold this method for now for other usage
def handleTestCreditsNormal(text, classesPerSemester, transferEquivalency): # To Handle Any Transfer Credits 
    semesterText = "Transfer"
    semesterYear = "Credits"
    for lineOfInformation in text:
        modifiedLine = lineOfInformation.replace(" ", "")
        if "TestTransGPA" in modifiedLine: break
        classNumberTracker = modifiedLine[3:6] # Find a class number
        try:
            int(classNumberTracker)
            classTitle = modifiedLine[0:3]
            createClassInformation(classTitle, classNumberTracker, semesterText, semesterYear, modifiedLine, classesPerSemester)
        except: # This might be incorrect, but we will see
            if classNumberTracker == "LVL":
                classTitle = modifiedLine[0:3]
                grabLevel = modifiedLine[6]
                createClassInformation(classTitle, f'LVL{str(grabLevel)}', semesterText, semesterYear, modifiedLine, classesPerSemester)
            else:
                list_of_keys = transferEquivalency.keys()
                classTitle = modifiedLine[0:3]
                for keys in list_of_keys:
                    if classTitle in keys: 
                        grabSBCValue = transferEquivalency[keys]
                        createClassInformation(classTitle, grabSBCValue, semesterText, semesterYear, modifiedLine, classesPerSemester)
            continue


@staticmethod
def createClassInformation(classTitle, classNumber, semesterText, semesterYear,  modifiedLine, classesPerSemester):
    dictInformation = parseSpecificClassInformation("", "", "", modifiedLine)
    ClassObject = SimpleClassObject(classTitle + " " + classNumber, dictInformation['classCreditsAmount'], dictInformation['classGrade'], semesterText, semesterYear)
    
    if semesterText + " " + semesterYear in classesPerSemester: # The Key Exists 
        getList = classesPerSemester[semesterText + " " + semesterYear]
        getList.append(ClassObject)
    else: # Does not exist, so we create a list for that particular semester
        listOfClassesInSemester = []
        listOfClassesInSemester.append(ClassObject)
        classesPerSemester[semesterText + " " + semesterYear] = listOfClassesInSemester
    

@staticmethod
def createClassObjectForMathCourses(classTitle, semesterText, semesterYear, modifiedLine, classNumber, mathRequiredCourses):
    dictInformation = parseSpecificClassInformation("", "", "", modifiedLine)
    MathObject = UniversalClassObject(classTitle + " " + classNumber + " (QPS)" if int(classNumber) < 200 else classTitle + " " +  classNumber + " (STEM+)", dictInformation['classGrade'], dictInformation['classCreditsAmount'], semesterText, semesterYear, dictInformation['classComments'])
    mathRequiredCourses[classTitle + " " + classNumber] = MathObject


@staticmethod
def createClassObjectForScienceCourses(classTitle, semesterText, semesterYear, modifiedLine, classNumber, scienceCourses):
    dictInformation = parseSpecificClassInformation("", "", "", modifiedLine)
    scienceObject = UniversalClassObject(classTitle + " " +  classNumber + " (SNW)" if int(classNumber) in [132, 131, 141, 152, 201, 102, 103, 122, 125, 127, 142] else (classTitle + " " + classNumber if int(classNumber) in [133, 204, 154, 322, 332, 112, 113, 134, 252] else classTitle + classNumber + " (STEM+)"), dictInformation['classGrade'], dictInformation['classCreditsAmount'], semesterText, semesterYear, dictInformation['classComments'])
    scienceCourses[classTitle + " " + classNumber] = scienceObject


@staticmethod
def createClassObjectForSBCCourses(classTitle, sbcLabel, semesterText, semesterYear, modifiedLine, classNumber, sbcCourses):
    dictInformation = parseSpecificClassInformation("", "", "", modifiedLine)
    SBCObject = SBCCourse(sbcLabel, classTitle + " " + classNumber, dictInformation['classGrade'], dictInformation['classCreditsAmount'], semesterText, semesterYear, dictInformation['classComments'])
    sbcCourses[classTitle + " " + classNumber] = SBCObject


@staticmethod
def parseSpecificClassInformation(classCreditsAmount, classGrade, classComments, modifiedLine) -> dict:
    indexOfColon = modifiedLine.index('.')
    modifiedLine = modifiedLine[indexOfColon+1::] 
    indexOfColonSecond = modifiedLine.index('.') # Find the second colon to signify the number of credits earned 
    modifiedLine = modifiedLine[indexOfColonSecond-1::]
    for characters in modifiedLine:
        if ((characters >= '0' and characters <= '9') or characters == '.') and len(classCreditsAmount) != 5: # We found the class attempted 
            classCreditsAmount += characters
        elif len(classCreditsAmount) == 5:
            if (characters >= 'A' and characters <= 'Z') or characters == '+' or characters == '-':
                if characters == 'I' or characters == 'W' or characters == 'Q':
                    classComments += characters
                    classGrade += characters # Might have side effects, so we will have to see 
                elif characters == 'T':
                    classGrade = "XFER"
                else:
                    if characters == '+':
                        classGrade += "+"
                    elif characters == '-':
                        classGrade += "-"
                    else:
                        classGrade += characters
    return {'classCreditsAmount': classCreditsAmount, 'classGrade': classGrade, 'classComments': classComments}