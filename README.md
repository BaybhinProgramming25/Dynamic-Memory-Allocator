The purpose of this code is to convert CSE Students at Stony Brook Univeristy PDF of their transcripts into a tabular, readable format. The code will parse the content in the transcript and will then generate three tables in an XLSX sheet. 

Note: There were some libraries used that may require downloading on the user-end.

Modules Used:
- threading
- PyPDF2
- os
- shututil
- openpyxl
- sys
- typing

How to Run The Code: 

1) Put any transcripts you wish to parse in the folder labeled 'input'

2) Within the 'src' folder, look for the python module titled 'Main'

3) Run the code in the module, prompting an input of the name of the transcript to be parsed in an input folder

4) Type in the name of the transcript with the input path specified and press 'Enter' (i.e. if you have a transcript in the input folder titled 'Example.pdf', then you would need to specify the user input as: input\Example.pdf

5) An XLSX sheet will be produced with the same name as the transcript in the 'output' folder

6) Repeat until requests have been satisifed, performing graceful termination by typing the word 'exit' pressing 'Enter'
