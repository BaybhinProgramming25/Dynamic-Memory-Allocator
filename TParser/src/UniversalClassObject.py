class UniversalClassObject: #Since all classes have the same structure, we can declare a universal class object
    def __init__(self, courseName, grade, credits, term, year, comments): #Constructor
        self.courseName = courseName
        self.grade = grade
        self.credits = credits
        self.term = term
        self.year = year
        self.comments = comments
    