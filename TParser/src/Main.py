import PyPDF2, os, threading, shutil, openpyxl
from CreateTabularDocument import * 
from StudentInfo import * 
from CumulativeInfo import *
from ParseClasses import *


def main():

        while True:
            directory = ""
            fileFound = 0
            while fileFound != 1:
                try:
                    directory = str(input("Please specify the path of the PDF (i.e. input\\NAMEOFFILE.pdf), otherwise type 'exit' to end the program: "))
                    if directory.lower() == "exit": break
                    if os.path.exists(directory) and directory.find(".pdf"):
                        with open(directory, "rb") as file:
                            pdf_reader = PyPDF2.PdfReader(file) #PdfFileReader is DEPRECATED so we use PdfReader instead
                            fileFound = 1
                    else:
                        print("Not Found!\n")
                except:
                    print("Please input a valid PDF path\n")

            if directory.lower() == "exit": 
                print("Program Ended!\n")
                break

            file = open(directory, "rb")
            pdf_reader = PyPDF2.PdfReader(file)
            totalPages = len(pdf_reader.pages)

            studentInformation, upperDivisionCourses, lowerDivisionCourses, technicalCSECourses, mathRequiredCourses, scienceCourses, sbcCourses, classesPerSemester = {}, {}, {}, {}, {}, {}, {}, {}  

            for i in range(totalPages):

                page = pdf_reader.pages[i]
                text = page.extract_text().split('\n') 

                #Have multiple threads to find the information concurrently 
                thread0 = threading.Thread(target=trackStudentInformation, args=(text, studentInformation))
                thread1 = threading.Thread(target=trackCumulativeInformation, args=(text, studentInformation))
                thread2 = threading.Thread(target=majorClassTracker, args=(text, upperDivisionCourses, lowerDivisionCourses, technicalCSECourses))
                thread3 = threading.Thread(target=mathTracker, args=(text, mathRequiredCourses))
                thread4 = threading.Thread(target=scienceTracker, args=(text, scienceCourses))
                thread5 = threading.Thread(target=sbcsTracker, args=(text, sbcCourses))
                thread6 = threading.Thread(target=classTracker, args=(text, classesPerSemester))

                thread0.start()
                thread1.start()
                thread2.start()
                thread3.start()
                thread4.start()
                thread5.start()
                thread6.start()

                thread0.join()
                thread1.join()
                thread2.join()
                thread3.join()
                thread4.join()
                thread5.join()
                thread6.join()


            # Now we need to create the file name, which we will do by just taking the name of the pdf file we made
            resetGlobalVariablesForStudentInfo() # Used to reset state variables that we have, probably could be a better approach to this so we might change this later 
            resetGlobalVariablesForCumulativeInformation() # Likewise, we need to take a better approach to this implementation
    

            grabSlash = directory.index('\\')
            grabPeriod = directory.index('.')
            fileNameInput = directory[grabSlash+1:grabPeriod]

            fileOpened = False 
            fileExists = False 

            if os.path.isfile(f'output\\{fileNameInput}.xlsx'): # If file exists
                fileExists = True
                try: 
                    wb = openpyxl.load_workbook(fileNameInput + '.xlsx', read_only=True)
                    with wb: # type: ignore
                        pass # File is not opened 
                except IOError: 
                    for filename in os.listdir('output'):
                        if filename.startswith(f'~${fileNameInput}.xlsx'):
                            fileOpened = True
                        else: # The file is not there, meaning it is closed
                            fileOpened = False

            if fileOpened == False or fileExists == False:
                    fileName = createDocument(fileNameInput, studentInformation, upperDivisionCourses, lowerDivisionCourses, technicalCSECourses, mathRequiredCourses, scienceCourses, sbcCourses, classesPerSemester) 

                    output_folder = "output\\"
                    shutil.move(fileName, output_folder + fileName) # Move the file to the output folder (hoping this works)

                    print(f'{fileName} has been created!')
            else: print("Please close the file first, then run the program again\n")

        
if __name__ == '__main__':
    main()
