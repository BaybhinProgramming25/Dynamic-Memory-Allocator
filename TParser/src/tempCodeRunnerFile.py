thread3 = threading.Thread(target=mathTracker, args=(text, mathRequiredCourses))
                thread4 = threading.Thread(target=scienceTracker, args=(text, scienceCourses))
                thread5 = threading.Thread(target=sbcsTracker, args=(text, sbcCourses))
                thread6 = threading.Thread(target=classTracker, args=(text, classesPerSemester))

                thread0.start()