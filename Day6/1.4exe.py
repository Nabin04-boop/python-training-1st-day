class student:
    def __init__(self, name, marks):
        self.name = name 
        self.marks = marks
    def results(self):
        if self.marks >= 40:
           return "pass"
        else:
            return "failed"
s1 = student("anita", 76)
s2 = student("ram", 38)
s3 = student("sita", 40)



print("s1", s1.results())
print("s2", s2.results())
print("s3", s3.results())