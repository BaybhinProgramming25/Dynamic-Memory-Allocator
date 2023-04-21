class SBCCourse:
    def __init__(self, sbc, courseName, grade, credits, term, year, comments): #Constructor
        self.sbc = sbc # This is going to be in the form of a list 
        self.courseName = courseName
        self.grade = grade
        self.credits = credits
        self.term = term
        self.year = year
        self.comments = comments